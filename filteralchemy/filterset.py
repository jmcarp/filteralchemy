# -*- coding: utf-8 -*-

import six
from marshmallow import fields
from marshmallow_sqlalchemy import ModelConverter

from filteralchemy import operators
from filteralchemy.filters import Filter
from filteralchemy.formatters import underscore_formatter

class FilterSetOptions(object):

    def __init__(self, meta):
        self.model = getattr(meta, 'model', None)
        self.query = getattr(meta, 'query', None)
        self.fields = getattr(meta, 'fields', ())
        self.exclude = getattr(meta, 'exclude', ())
        self.list_class = getattr(meta, 'list_class', fields.List)
        self.converter = getattr(meta, 'converter', ModelConverter())
        self.operators = getattr(meta, 'operators', (operators.Equal, ))
        self.formatter = getattr(meta, 'formatter', underscore_formatter)
        self.parser = getattr(meta, 'parser', None)

class FilterSetMeta(type):

    def __new__(mcs, name, bases, attrs):
        declared_fields = mcs.get_declared_filters(attrs)
        klass = super(FilterSetMeta, mcs).__new__(mcs, name, bases, attrs)
        klass.opts = FilterSetOptions(getattr(klass, 'Meta'))
        klass.filters = dict(
            declared_fields +
            mcs.get_inherited_filters(klass) +
            mcs.get_model_filters(klass)
        )
        return klass

    def get_declared_filters(attrs):
        return [
            (key, attrs.pop(key))
            for key, value in list(attrs.items())
            if isinstance(value, Filter)
        ]

    def get_inherited_filters(mcs):
        return [
            (key, value)
            for parent in mcs.mro()[:0:-1]
            for key, value in getattr(parent, 'filters', parent.__dict__).items()
            if isinstance(value, Filter)
        ]

    def get_model_filters(klass):
        opts = klass.opts
        if not opts.model:
            return []
        filters = []
        for prop in opts.model.__mapper__.iterate_properties:
            field = opts.converter.field_for(opts.model, prop.key)
            for operator in opts.operators:
                name = underscore_formatter(prop.key, operator)
                label = opts.formatter(prop.key, operator)
                filter_ = Filter(prop.key, field, label=label, operator=operator)
                filters.append((name, filter_))
        return filters

class FilterSet(six.with_metaclass(FilterSetMeta, object)):

    class Meta:
        pass

    def filter(self):
        argmap = {
            filter.label or label: filter.field
            for label, filter in self.filters.items()
        }
        args = self.opts.parser.parse(argmap)
        query = self.opts.query
        for label, filter in self.filters.items():
            value = args.get(filter.label or label)
            if value is not None:
                query = filter.filter(query, self.opts.model, value)
        return query
