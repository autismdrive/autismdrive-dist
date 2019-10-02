import datetime

import flask_restful
from flask import request
from marshmallow import ValidationError

from app import RestException, db, elastic_index
from app.model.location import Location
from app.schema.schema import LocationSchema


class LocationEndpoint(flask_restful.Resource):

    schema = LocationSchema()

    def get(self, id):
        model = db.session.query(Location).filter_by(id=id).first()
        if model is None: raise RestException(RestException.NOT_FOUND)
        return self.schema.dump(model)

    def delete(self, id):
        location = db.session.query(Location).filter_by(id=id).first()

        if location is not None:
            elastic_index.remove_document(location, 'Location')

        db.session.query(Location).filter_by(id=id).delete()
        db.session.commit()
        return None

    def put(self, id):
        request_data = request.get_json()
        instance = db.session.query(Location).filter_by(id=id).first()
        updated, errors = self.schema.load(request_data, instance=instance)
        if errors: raise RestException(RestException.INVALID_OBJECT, details=errors)
        updated.last_updated = datetime.datetime.now()
        db.session.add(updated)
        db.session.commit()
        elastic_index.update_document(updated, 'Location', latitude=updated.latitude, longitude=updated.longitude)
        return self.schema.dump(updated)


class LocationListEndpoint(flask_restful.Resource):

    locationsSchema = LocationSchema(many=True)
    locationSchema = LocationSchema()

    def get(self):
        locations = db.session.query(Location).all()
        return self.locationsSchema.dump(locations)

    def post(self):
        request_data = request.get_json()
        try:
            load_result = self.locationSchema.load(request_data).data
            db.session.add(load_result)
            db.session.commit()
            elastic_index.add_document(load_result, 'Location', latitude=load_result.latitude, longitude=load_result.longitude)
            return self.locationSchema.dump(load_result)
        except ValidationError as err:
            raise RestException(RestException.INVALID_OBJECT,
                                details=load_result.errors)
