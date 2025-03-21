from datetime import datetime, timedelta
from dateutil import tz

from app.model.role import Permission
from elasticsearch import RequestError
from elasticsearch_dsl import Date, Keyword, Text, Index, analyzer, Integer, tokenizer, Document, Double, GeoPoint, \
    Search, A, Q, Boolean, analysis
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.query import MultiMatch, MatchAll, MoreLikeThis
from flask import g
import logging

autocomplete = analyzer('autocomplete',
                        tokenizer=tokenizer('ngram', 'edge_ngram', min_gram=2, max_gram=15,
                                            token_chars=["letter", "digit"]),
                        filter=['lowercase']
                        )
autocomplete_search = analyzer('autocomplete_search',
                               tokenizer=tokenizer('lowercase')
                               )

english_stem_filter = analysis.token_filter('my_english_filter', name="minimal_english", type="stemmer")
stem_analyzer = analyzer('stem_analyzer',
                        tokenizer=tokenizer('standard'),
                        filter=['lowercase', english_stem_filter])


# Star Documents are ElasticSearch documents and can be used to index an Event,
# Location, Resource, or Study
class StarDocument(Document):
    type = Keyword()
    label = Keyword()
    id = Integer()
    title = Text()
    date = Date()
    last_updated = Date()
    content = Text(analyzer=stem_analyzer)
    description = Text()
    post_event_description = Text()
    organization_name = Keyword()
    website = Keyword()
    location = Keyword()
    ages = Keyword(multi=True)
    languages = Keyword(multi=True)
    status = Keyword()
    category = Keyword(multi=True)
    latitude = Double()
    longitude = Double()
    geo_point = GeoPoint()
    status = Keyword()
    no_address = Boolean()
    is_draft = Boolean()


def _start_of_day(date=datetime.utcnow().date()):
    return datetime(date.year, date.month, date.day, tzinfo=tz.tzutc())


class ElasticIndex:

    logger = logging.getLogger("ElasticIndex")

    def __init__(self, app):
        self.logger.debug("Initializing Elastic Index")
        self.establish_connection(app.config['ELASTIC_SEARCH'])
        self.index_prefix = app.config['ELASTIC_SEARCH']["index_prefix"]

        self.index_name = '%s_resources' % self.index_prefix
        self.index = Index(self.index_name)
        self.index.doc_type(StarDocument)
        try:
            self.index.create()
        except RequestError as requestError:
            if requestError.error == 'resource_already_exists_exception':
                self.logger.info("The index already exists.")
            else:
                self.logger.fatal("Error Creating Index. ")
                raise requestError
        except Exception as e:
            self.logger.info("Failed to create the index(s).  They may already exist." + str(e))

    def establish_connection(self, settings):
        """Establish connection to an ElasticSearch host, and initialize the Submission collection"""
        if settings["http_auth_user"] != '':
            self.connection = connections.create_connection(
                hosts=settings["hosts"],
                port=settings["port"],
                timeout=settings["timeout"],
                verify_certs=settings["verify_certs"],
                use_ssl=settings["use_ssl"],
                http_auth=(settings["http_auth_user"],
                           settings["http_auth_pass"]))
        else:
            # Don't set an http_auth at all for connecting to AWS ElasticSearch or you will
            # get a cryptic message that is darn near ungoogleable.
            self.connection = connections.create_connection(
                hosts=settings["hosts"],
                port=settings["port"],
                timeout=settings["timeout"],
                verify_certs=settings["verify_certs"],
                use_ssl=settings["use_ssl"])

    def clear(self):
        try:
            self.logger.info("Clearing the index.")
            self.index.delete(ignore=404)
            self.index.create()
        except:
            self.logger.error("Failed to delete the indices. They might not exist.")

    def remove_document(self, document, flush=True):
        obj = self.get_document(document)
        obj.delete()
        if flush:
            self.index.flush()

    @staticmethod
    def _get_id(document):
        return document.__tablename__.lower() + '_' + str(document.id)

    def get_document(self, document):
        uid = self._get_id(document)
        return StarDocument.get(id=uid, index=self.index_name)

    def update_document(self, document, flush=True, latitude=None, longitude=None):
        # update is the same as add, as it will overwrite.  Better to have code in one place.
        self.add_document(document, flush, latitude, longitude)

    def add_document(self, document, flush=True, latitude=None, longitude=None, post_event_description=None):
        doc = StarDocument(id=document.id,
                           type=document.__tablename__,
                           label=document.__label__,
                           title=document.title,
                           last_updated=document.last_updated,
                           content=document.indexable_content(),
                           description=document.description,
                           post_event_description=post_event_description,
                           organization_name=document.organization_name,
                           location=None,
                           ages=document.ages,
                           status=None,
                           category=[],
                           latitude=None,
                           longitude=None,
                           geo_point=None
                           )

        if hasattr(document, 'date'):
            doc.date = document.date
        if hasattr(document, 'post_event_description'):
            doc.post_event_description = document.post_event_description
        if hasattr(document, 'languages'):
            doc.languages = document.languages
        if hasattr(document, 'website'):
            doc.website = document.website
        if hasattr(document, 'is_draft'):
            doc.is_draft = document.is_draft
        if hasattr(document, 'status') and document.status is not None:
            doc.status = document.status.value
        if hasattr(document, 'city') and document.city is not None:
            doc.content = doc.content + " " + document.city

        doc.meta.id = self._get_id(document)

        for cat in document.categories:
            doc.category.extend(cat.category.all_search_paths())

        if document.__tablename__ == 'study':
            doc.title = document.short_title
            doc.description = document.short_description

        if (doc.type in ['location', 'event']) and None not in (latitude, longitude):
            doc.latitude = latitude
            doc.longitude = longitude
            doc.geo_point = dict(lat=latitude, lon=longitude)
            doc.no_address = not document.street_address1

        StarDocument.save(doc, index=self.index_name)
        if flush:
            self.index.flush()

    def load_documents(self, resources, events, locations, studies):
        self.logger.info("Loading search records of events, locations, resources, and studies into Elasticsearch index: %s" % self.index_prefix)
        for r in resources:
            self.add_document(r, flush=False)
        for e in events:
            post_event_description = e.post_event_description if hasattr(e, 'post_event_description') else None
            self.add_document(e, flush=False, latitude=e.latitude, longitude=e.longitude, post_event_description=post_event_description)
        for l in locations:
            self.add_document(l, flush=False, latitude=l.latitude, longitude=l.longitude)
        for s in studies:
            self.add_document(s, flush=False)
        self.index.flush()

    def search(self, search):
        sort = None if search.sort is None else search.sort.translate()

        if not search.words:
            query = MatchAll()
        else:
            query = MultiMatch(query=search.words, fields=['content'])

        elastic_search = Search(index=self.index_name)\
            .doc_type(StarDocument)\
            .query(query)\
            .highlight('content', type='unified', fragment_size=150)

        elastic_search = elastic_search[search.start:search.start + search.size]

        # Filter results for type, ages, and languages
        if search.types:
            if set(search.types) == {'resource'}:
                # Include past events in resource search results
                search.types.append('event')

            elastic_search = elastic_search.filter('terms', **{"type": search.types})
        if search.ages:
            elastic_search = elastic_search.filter('terms', **{"ages": search.ages})
        if search.languages:
            elastic_search = elastic_search.filter('terms', **{"languages": search.languages})

        if set(search.types) == {'resource', 'event'}:
            # Include past events in resource search results
            elastic_search = elastic_search.filter('bool', **{"should": [
                self._past_events_filter(),  # Past events OR
                self._non_events_filter(),   # Date field is empty
            ]})
        elif search.date:
            # Filter results by date
            elastic_search = elastic_search.filter('range', **{"date": {"gte": _start_of_day(search.date)}})
        elif set(search.types) == {'event'}:
            elastic_search = elastic_search.filter('bool', **{"should": self._future_events_filter()})
        else:
            elastic_search = elastic_search.filter('bool', **{"should": self._default_filter()})

        if search.geo_box:

            # Make sure the GeoBox is at least a square mile.
            b = search.geo_box
            min_size = 0.016667  # 1 degree minute = approx. 1 mile
            lat_offset = 0 if (b.top_left.lat - b.bottom_right.lat) > min_size else min_size/2
            lon_offset = 0 if (b.top_left.lon - b.bottom_right.lon) > min_size else min_size/2

            elastic_search = elastic_search.filter('geo_bounding_box', **{"geo_point": {
                        "top_left" : {
                            "lat" : b.top_left.lat - lat_offset,
                            "lon" : b.top_left.lon - lon_offset,
                        },
                        "bottom_right" : {
                            "lat" : b.bottom_right.lat + lat_offset,
                            "lon" : b.bottom_right.lon + lon_offset
                        }
                    }})

        if sort is not None:
            elastic_search = elastic_search.sort(sort)

        if 'user' in g and g.user:
            if Permission.edit_resource not in g.user.role.permissions():
                elastic_search = elastic_search.filter(Q('bool', must_not=[Q('match', is_draft=True)]))
        else:
            elastic_search = elastic_search.filter(Q('bool', must_not=[Q('match', is_draft=True)]))

        if search.category and search.category.id:
            elastic_search = elastic_search.filter('terms', category=[str(search.category.search_path())])
            if search.category.calculate_level() == 0:
                exclude = ".*\\,.*\\,.*"
                include = str(search.category.id) + "\\,.*"
                aggregation = A("terms", field='category', exclude=exclude, include=include, size=25)
            elif search.category.calculate_level() == 1:
                include = ".*\\,.*\\,.*"
                aggregation = A("terms", field='category', include=include, size=25)
            else:
                aggregation = A("terms", field='category', size=25)
        else:
            aggregation = A("terms", field='category', exclude=".*\\,.*", size=25)

        elastic_search.aggs.bucket('terms', aggregation)
        elastic_search.aggs.bucket('type', A("terms", field='type'))
        elastic_search.aggs.bucket('ages', A("terms", field='ages'))
        elastic_search.aggs.bucket('languages', A("terms", field='languages'))

        # KEEPING FOR NOW - THESE WERE THE ORIGINAL FACETS WE HAD SET UP.  WILL NEED TO CONVERT TO AGGREGATIONS
        # IF WE WANT TO KEEP ANY OF THESE.
        # 'Location': elasticsearch_dsl.TermsFacet(field='location'),
        # 'Type': elasticsearch_dsl.TermsFacet(field='label'),
        # 'Age Range': elasticsearch_dsl.TermsFacet(field='age_range'),
        # 'Category': elasticsearch_dsl.TermsFacet(field='category'),
        # 'Organization': elasticsearch_dsl.TermsFacet(field='organization'),
        # 'Status': elasticsearch_dsl.TermsFacet(field='status'),
        # 'Topic': elasticsearch_dsl.TermsFacet(field='topic'),

        return elastic_search.execute()

    # Finds all resources related to the given item.
    def more_like_this(self, item, max_hits=3):

        query = MoreLikeThis(
            like=[
                # {'_id': ElasticIndex._get_id(item), '_index': self.index_name},
                item.indexable_content(),
                item.category_names()
            ],
            min_term_freq=1,
            min_doc_freq=2,
            max_query_terms=12,
            fields=['title', 'content', 'description', 'location', 'category', 'organization_name', 'website'])

        elastic_search = Search(index=self.index_name)\
            .doc_type(StarDocument)\
            .query(query)

        elastic_search = elastic_search[0:max_hits]

        # Filter out past events
        elastic_search = elastic_search.filter('bool', **{"should": self._default_filter()})

        return elastic_search.execute()

    # Past events with a non-empty post-event description
    def _past_events_filter(self):
        return {
            "bool": {
                "filter": [
                    {"terms": {"type": ["event"]}},
                    {"exists": {"field": "post_event_description"}},
                    {"range": {"date": {"lt": _start_of_day()}}},
                ]
            }
        }

    # Future events
    def _future_events_filter(self):
        return {
            "bool": {
                "filter": [
                    {"terms": {"type": ["event"]}},
                    {"range": {"date": {"gte": _start_of_day()}}},
                ]
            }
        }

    # Non-events (i.e., date field is empty)
    def _non_events_filter(self):
        return {"bool": {"must_not": {"exists": {"field": "date"}}}}

    # Past events, future events, and non-events
    def _default_filter(self):
        return [
            self._past_events_filter(),
            self._future_events_filter(),
            self._non_events_filter(),
        ]


