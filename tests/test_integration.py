# -*- coding: utf-8 -*-

import datetime

import flask
import pytest
from webargs import fields
from webargs.flaskparser import parser

from filteralchemy import operators
from filteralchemy import formatters
from filteralchemy.filters import Filter
from filteralchemy.filterset import FilterSet

@pytest.fixture
def app():
    return flask.Flask(__name__)

class TestFilters:

    @pytest.fixture
    def ModelFilterSet(self, session, models):
        def modulo(query, model, attr, value):
            return query.filter(model.sales % value == 0)
        class ModelFilterSet(FilterSet):
            class Meta:
                model = models.Album
                query = session.query(models.Album)
                operators = (operators.Equal, operators.In)
                parser = parser
            name__like = Filter('name', fields.Str(), operator=operators.Like)
            sales__modulo = Filter(field=fields.Str(), operator=modulo)
        return ModelFilterSet

    @pytest.fixture
    def albums(self, models, session):
        albums = [
            models.Album(
                name='A Night at the Opera',
                date=datetime.date(1975, 11, 21),
                sales=12000000,
            ),
            models.Album(
                name='The Works',
                date=datetime.date(1984, 2, 27),
                sales=5000000,
            ),
        ]
        for album in albums:
            session.add(album)
        session.commit()
        return albums

    def test_filter_none(self, app, albums, session, ModelFilterSet):
        with app.test_request_context('/'):
            query = ModelFilterSet().filter()
            assert set(query.all()) == set(albums)

    def test_filter_equal(self, app, albums, session, ModelFilterSet):
        with app.test_request_context('/?name=The Works'):
            query = ModelFilterSet().filter()
            assert query.count() == 1
            assert query.first() == albums[1]

    def test_filter_equal_date(self, app, albums, session, ModelFilterSet):
        with app.test_request_context('/?date=1984-02-27'):
            query = ModelFilterSet().filter()
            assert query.count() == 1
            assert query.first() == albums[1]

    def test_filter_in(self, app, albums, session, ModelFilterSet):
        with app.test_request_context('/?sales__in=12000000&sales__in=5000000'):
            query = ModelFilterSet().filter()
            assert set(query.all()) == set(albums)

    def test_declared_filter(self, app, albums, session, ModelFilterSet):
        with app.test_request_context('/?name__like=%Night%'):
            query = ModelFilterSet().filter()
            assert query.count() == 1
            assert query.first() == albums[0]

    def test_custom_filter(self, app, albums, session, ModelFilterSet):
        with app.test_request_context('/?sales__modulo=3000000'):
            query = ModelFilterSet().filter()
            assert query.count() == 1
            assert query.first() == albums[0]

    def test_custom_formatter(self, app, albums, models, session):
        class ModelFilterSet(FilterSet):
            class Meta:
                model = models.Album
                query = session.query(models.Album)
                formatter = formatters.JsonApiFormatter()
                operators = (operators.Equal, operators.NotEqual)
                parser = parser
        with app.test_request_context('/?filter[name][ne]=The Works'):
            query = ModelFilterSet().filter()
            assert query.count() == 1
            assert query.first() == albums[0]
