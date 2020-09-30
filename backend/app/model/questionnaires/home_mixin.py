import datetime

from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr

from app import db
from app.model.questionnaires.housemate import Housemate
from app.export_service import ExportService


class HomeMixin(object):
    __question_type__ = ExportService.TYPE_UNRESTRICTED
    __estimated_duration_minutes__ = 5

    id = db.Column(db.Integer, primary_key=True)
    last_updated = db.Column(db.DateTime(timezone=True), default=func.now())
    time_on_task_ms = db.Column(db.BigInteger, default=0)

    @declared_attr
    def participant_id(cls):
        return db.Column("participant_id", db.Integer, db.ForeignKey("stardrive_participant.id"))

    @declared_attr
    def user_id(cls):
        return db.Column("user_id", db.Integer, db.ForeignKey("stardrive_user.id"))

    @declared_attr
    def housemates(cls):
        return db.relationship(
            "Housemate",
            backref=db.backref(cls.__tablename__, lazy=True),
            cascade="all, delete-orphan",
            passive_deletes=True
        )

    @declared_attr
    def struggle_to_afford(cls):
        return db.Column(
            db.Boolean,
            info={
                "display_order": 4,
                "type": "radio",
                "template_options": {
                    "required": False,
                    "label": 'Financial Struggles',
                    "options": [
                        {"value": True, "label": "Yes"},
                        {"value": False, "label": "No"},
                    ],
                },
                "expression_properties": {
                    "template_options.description": cls.struggle_to_afford_desc
                },
            },
        )

    def get_field_groups(self):
        field_groups = {
                "housemates": {
                    "type": "repeat",
                    "display_order": 3,
                    "wrappers": ["card"],
                    "repeat_class": Housemate,
                    "template_options": {
                        "label": "Who else lives there?",
                        "description": "Add a housemate",
                    },
                    "expression_properties": {},
                },
            }
        return field_groups
