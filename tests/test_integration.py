# -*- coding: utf-8 -*-

from filteralchemy import operators
from filteralchemy.filterset import FilterSet

def get_labels(klass):
    return set(filter_.label for filter_ in klass.filters.values())

class TestFilterSet:

    def test_default_fields(self, models):
        class ModelFilterSet(FilterSet):
            class Meta:
                model = models.Album
        expected = set(models.Album.__mapper__.columns.keys())
        assert expected == get_labels(ModelFilterSet)

    def test_default_operator(self, models):
        class ModelFilterSet(FilterSet):
            class Meta:
                model = models.Album
                default_operator = operators.In
                operators = (operators.Equal, operators.In)
        expected = set(
            '{}{}'.format(key, suffix)
            for key in models.Album.__mapper__.columns.keys()
            for suffix in ('', '__eq')
        )
        assert expected == get_labels(ModelFilterSet)

    def test_fields(self, models):
        class ModelFilterSet(FilterSet):
            class Meta:
                model = models.Album
                fields = ('id', 'name', 'genre')
        assert {'id', 'name', 'genre'} == get_labels(ModelFilterSet)

    def test_exclude(self, models):
        class ModelFilterSet(FilterSet):
            class Meta:
                model = models.Album
                exclude = ('sales', 'date')
        assert {'id', 'name', 'genre'} == get_labels(ModelFilterSet)
