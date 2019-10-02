import datetime

from dateutil.tz import tzutc
from sqlalchemy import func

from app import db


class Organization(db.Model):
    __tablename__ = 'organization'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    last_updated = db.Column(db.DateTime(timezone=True), default=func.now())
    description = db.Column(db.String)
    resources = db.relationship(
        'Resource', backref=db.backref('organization', lazy=True))
    studies = db.relationship(
        'Study', backref=db.backref('organization', lazy=True))
    investigators = db.relationship(
        'Investigator', backref=db.backref('organization', lazy=True))
