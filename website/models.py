from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.inspection import inspect


class Serializer(object):

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]


class User(db.Model, UserMixin, Serializer):
    __table__ = db.Model.metadata.tables['User']

    def serialize(self):
        d = Serializer.serialize(self)
        del d['password']
        return d


class Customer(db.Model, Serializer):
    __table__ = db.Model.metadata.tables['User_customers']

    def serialize(self):
        d = Serializer.serialize(self)
        return d


class User_datasources_tokens(db.Model, Serializer):
    __table__ = db.Model.metadata.tables['User_datasources_tokens']

    def serialize(self):
        d = Serializer.serialize(self)
        return d


class User_datasources(db.Model, Serializer):
    __table__ = db.Model.metadata.tables['User_datasources']

    def serialize(self):
        d = Serializer.serialize(self)
        return d


'''
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
'''
