# -*- coding: utf-8 -*-

import pytest

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

class Bunch(object):
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

@pytest.fixture
def Base():
    return declarative_base()

@pytest.fixture
def session(Base):
    engine = sa.create_engine('sqlite:///:memory:')
    Session = sa.orm.sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    return Session()

@pytest.fixture
def models(Base):
    class Album(Base):
        __tablename__ = 'album'
        id = sa.Column(sa.Integer, primary_key=True)

        name = sa.Column(sa.String)
        genre = sa.Column(sa.String)
        sales = sa.Column(sa.Float)
        date = sa.Column(sa.Date)
    return Bunch(Album=Album)
