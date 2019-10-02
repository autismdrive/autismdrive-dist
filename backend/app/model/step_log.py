import datetime

from dateutil.tz import tzutc
from flask_marshmallow.sqla import ModelSchema
from sqlalchemy import func

from app import db


class StepLog(db.Model):
    __tablename__ = 'step_log'
    id = db.Column(db.Integer, primary_key=True)
    questionnaire_name = db.Column(db.String)
    questionnaire_id = db.Column(db.Integer)
    flow = db.Column(db.String)
    participant_id = db.Column('participant_id', db.Integer, db.ForeignKey('stardrive_participant.id'))
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('stardrive_user.id'))
    date_completed = db.Column(db.DateTime(timezone=True), default=func.now())
    time_on_task_ms = db.Column(db.BigInteger)
    last_updated = db.Column(db.DateTime(timezone=True), default=func.now())


