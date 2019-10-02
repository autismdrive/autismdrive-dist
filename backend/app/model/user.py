import datetime
import jwt
import enum

from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property

from app import app, db, RestException, bcrypt
from app.model.participant import Participant

from random import randint


def random_integer():
    min_ = 100
    max_ = 1000000000
    rand = randint(min_, max_)

    # possibility of same random number is very low.
    # but if you want to make sure, here you can check id exists in database.
    while db.session.query(User).filter(id == rand).limit(1).first() is not None:
        rand = randint(min_, max_)

    return rand

class Role(enum.Enum):
    admin = 1
    user = 2

    @classmethod
    def has_name(cls, name):
        return any(name == item.name for item in cls)

    @classmethod
    def options(cls):
        return [item.name for item in cls]


class User(db.Model):
    # The user model is used to manage interaction with the StarDrive system, including sign-in and access levels. Users
    # can be Admins, people with autism and/or their guardians wishing to manage their care and participate in studies,
    # as well professionals in the field of autism research and care. Anyone who wishes to use the system will have a
    # user account. Please note that there is a separate participant model for tracking enrollment and participation in
    # studies.
    __tablename__ = 'stardrive_user'
#    id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, primary_key=True, default=random_integer)
    last_updated = db.Column(db.DateTime(timezone=True), default=func.now())
    email = db.Column(db.String, nullable=False, unique=True)
    role = db.Column(db.Enum(Role))
    participants = db.relationship(Participant, back_populates="user")
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    _password = db.Column('password', db.Binary(60))
    token = ''

    def related_to_participant(self, participant_id):
        for p in self.participants:
            if p.id == participant_id:
                return True
        return False

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def is_correct_password(self, plaintext):
        if not self._password:
            raise RestException(RestException.LOGIN_FAILURE)
        return bcrypt.check_password_hash(self._password, plaintext)

    def encode_auth_token(self):
        try:
            payload = {
                'exp':
                    datetime.datetime.utcnow() + datetime.timedelta(
                        hours=2, minutes=0, seconds=0),
                'iat':
                    datetime.datetime.utcnow(),
                'sub':
                    self.id
            }
            return jwt.encode(
                payload, app.config.get('SECRET_KEY'), algorithm='HS256')
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(
                auth_token, app.config.get('SECRET_KEY'), algorithms='HS256')
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise RestException(RestException.TOKEN_EXPIRED)
        except jwt.InvalidTokenError:
            raise RestException(RestException.TOKEN_INVALID)

    def get_contact(self):
        for p in self.participants:
            if p.contact:
                return {'name': p.get_name(), 'relationship': p.relationship.name, 'contact': p.contact}
