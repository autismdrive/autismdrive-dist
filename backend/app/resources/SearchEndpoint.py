import elasticsearch
import flask_restful
from flask import request, json

from app import elastic_index, RestException, db
from app.model.category import Category
from app.model.search import Hit
from app.schema.schema import SearchSchema


class SearchEndpoint(flask_restful.Resource):
    def __post__(self, result_types = None):
        request_data = request.get_json()

        # Handle some sloppy category data.
        if 'category' in request_data and (not request_data['category'] or not request_data['category']['id']):
            del request_data['category']

        search, errors = SearchSchema().load(request_data)

        if errors:
            raise RestException(RestException.INVALID_OBJECT, details=errors)
        try:
            # Overwrite the result types if requested.
            if not search.types and result_types:
                search.types = result_types
            results = elastic_index.search(search)
        except elasticsearch.ElasticsearchException as e:
            raise RestException(RestException.ELASTIC_ERROR, details=json.dumps(e.info))

        search.reset()  # zero out any existing counts or data on the search prior to populating.
        search.total = results.hits.total
        search.category = self.update_category_counts(search.category, results)
        self.update_aggregations(search, results.aggregations)

        search.hits = []
        for hit in results:
            highlights = ""
            if "highlight" in hit.meta:
                highlights = "... ".join(hit.meta.highlight.content)
            hit = Hit(hit.id, hit.content, hit.description, hit.title, hit.type, hit.label, hit.date, hit.last_updated,
                      highlights, hit.latitude, hit.longitude, hit.status)
            search.hits.append(hit)

        return SearchSchema().jsonify(search)

    def update_aggregations(self, search, aggregations):
        for bucket in aggregations.ages.buckets:
            search.add_aggregation("ages", bucket.key, bucket.doc_count, bucket.key in search.ages)
        for bucket in aggregations.type.buckets:
            search.add_aggregation("types", bucket.key, bucket.doc_count, bucket.key in search.types)

    # given a results of a search, creates the appropriate category.
    # Also assures that there is a category at the top called "TOP".
    def update_category_counts(self, category, results):
        if not category:
            category = Category(name="Topics")
            category.children = db.session.query(Category)\
                .filter(Category.parent_id == None)\
                .order_by(Category.name)\
                .all()
        else:
            c = category
            while c.parent:
                c = c.parent
            c.parent = Category(name="Topics")

        for child in category.children:
            for bucket in results.aggregations.terms.buckets:
                if bucket.key == child.search_path():
                    child.hit_count = bucket.doc_count
        return category

    def post(self):
        return self.__post__()