import datetime

import flask_restful
from flask import request, g
from marshmallow import ValidationError

from app import RestException, db, elastic_index, auth
from app.model.event import Event
from app.model.resource_change_log import ResourceChangeLog
from app.schema.schema import EventSchema
from app.model.user import Role
from app.wrappers import requires_roles


class EventEndpoint(flask_restful.Resource):

    schema = EventSchema()

    def get(self, id):
        model = db.session.query(Event).filter_by(id=id).first()
        if model is None: raise RestException(RestException.NOT_FOUND)
        return self.schema.dump(model)

    @auth.login_required
    @requires_roles(Role.admin)
    def delete(self, id):
        event = db.session.query(Event).filter_by(id=id).first()
        event_id = event.id
        event_title = event.title

        if event is not None:
            elastic_index.remove_document(event, 'Event')

        db.session.query(Event).filter_by(id=id).delete()
        db.session.commit()
        self.log_update(event_id=event_id, event_title=event_title, change_type='delete')
        return None

    @auth.login_required
    @requires_roles(Role.admin)
    def put(self, id):
        request_data = request.get_json()
        instance = db.session.query(Event).filter_by(id=id).first()
        updated, errors = self.schema.load(request_data, instance=instance)
        if errors: raise RestException(RestException.INVALID_OBJECT, details=errors)
        updated.last_updated = datetime.datetime.now()
        db.session.add(updated)
        db.session.commit()
        elastic_index.update_document(updated, 'Event', latitude=updated.latitude, longitude=updated.longitude)
        self.log_update(event_id=updated.id, event_title=updated.title, change_type='edit')
        return self.schema.dump(updated)

    def log_update(self, event_id, event_title, change_type):
        log = ResourceChangeLog(resource_id=event_id, resource_title=event_title, user_id=g.user.id,
                                user_email=g.user.email, type=change_type)
        db.session.add(log)
        db.session.commit()


class EventListEndpoint(flask_restful.Resource):

    eventsSchema = EventSchema(many=True)
    eventSchema = EventSchema()

    def get(self):
        events = db.session.query(Event).all()
        return self.eventsSchema.dump(events)

    @auth.login_required
    @requires_roles(Role.admin)
    def post(self):
        request_data = request.get_json()
        try:
            load_result = self.eventSchema.load(request_data).data
            db.session.add(load_result)
            db.session.commit()
            elastic_index.add_document(load_result, 'Event', latitude=load_result.latitude, longitude=load_result.longitude)
            self.log_update(event_id=load_result.id, event_title=load_result.title, change_type='create')
            return self.eventSchema.dump(load_result)
        except ValidationError as err:
            raise RestException(RestException.INVALID_OBJECT,
                                details=load_result.errors)

    def log_update(self, event_id, event_title, change_type):
        log = ResourceChangeLog(resource_id=event_id, resource_title=event_title, user_id=g.user.id,
                                user_email=g.user.email, type=change_type)
        db.session.add(log)
        db.session.commit()
