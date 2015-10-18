# -*- coding: utf-8 -*-

from filteralchemy.filterset import FilterSet

class TestFilterSet:

    def test_default_fields(self, models):
        class ModelFilterSet(FilterSet):
            class Meta:
                model = models.Album
        expected = set(models.Album.__mapper__.columns.keys())
        assert set(ModelFilterSet.filters.keys()) == expected

    def test_fields(self, models):
        class ModelFilterSet(FilterSet):
            class Meta:
                model = models.Album
                fields = ('id', 'name', 'genre')
        assert set(ModelFilterSet.filters.keys()) == {'id', 'name', 'genre'}

    def test_exclude(self, models):
        class ModelFilterSet(FilterSet):
            class Meta:
                model = models.Album
                exclude = ('sales', 'date')
        assert set(ModelFilterSet.filters.keys()) == {'id', 'name', 'genre'}
