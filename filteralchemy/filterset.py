# -*- coding: utf-8 -*-

import six
from marshmallow import fields
from marshmallow_sqlalchemy import ModelConverter

from filteralchemy import Filter, operators
from filteralchemy.formatters import underscore_formatter

def call_or_value(value, *args, **kwargs):
    return value(*args, **kwargs) if callable(value) else value

class FilterSetOptions(object):

    def __init__(self, meta):
        self.model = getattr(meta, 'model', None)
        self.query = getattr(meta, 'query', None)
        self.fields = getattr(meta, 'fields', ())
        self.exclude = getattr(meta, 'exclude', ())
        self.list_class = getattr(meta, 'list_class', fields.List)
        self.converter = getattr(meta, 'converter', ModelConverter())
        self.operators = getattr(meta, 'operators', (operators.Equal, ))
        self.default_operator = getattr(meta, 'default_operator', operators.Equal)
        self.formatter = getattr(meta, 'formatter', underscore_formatter)
        self.column_overrides = getattr(meta, 'column_overrides', {})
        self.parser = getattr(meta, 'parser', None)

class FilterSetMeta(type):

    def __new__(mcs, name, bases, attrs):
        declared_fields = mcs.get_declared_filters(attrs)
        klass = super(FilterSetMeta, mcs).__new__(mcs, name, bases, attrs)
        klass.opts = FilterSetOptions(getattr(klass, 'Meta'))
        klass.filters = dict(
            mcs.get_model_filters(klass) +
            mcs.get_inherited_filters(klass) +
            declared_fields
        )
        return klass

    @classmethod
    def get_declared_filters(mcs, attrs):
        return [
            (key, attrs.pop(key))
            for key, value in list(attrs.items())
            if isinstance(value, Filter)
        ]

    @classmethod
    def get_inherited_filters(mcs, klass):
        return [
            (key, value)
            for parent in klass.mro()[:0:-1]
            for key, value in getattr(parent, 'filters', parent.__dict__).items()
            if isinstance(value, Filter)
        ]

    @classmethod
    def get_model_filters(mcs, klass):
        opts = klass.opts
        if not opts.model:
            return []
        properties = list(opts.model.__mapper__.iterate_properties)
        fields = call_or_value(opts.fields, klass=klass)
        exclude = call_or_value(opts.exclude, klass=klass)
        keys = set(
            fields or
            [prop.key for prop in properties]
        ).difference(exclude)
        filters = []
        for prop in properties:
            if prop.key not in keys:
                continue
            overrides = opts.column_overrides.get(prop.key, {})
            field = (
                overrides.get('field') or
                opts.converter.field_for(opts.model, prop.key)
            )
            operators = overrides.get('operators') or opts.operators
            for operator in operators:
                operator_name = (
                    operator.label
                    if operator != opts.default_operator
                    else None
                )
                name = underscore_formatter(prop.key, operator_name)
                label = opts.formatter(prop.key, operator_name)
                filter_ = mcs.make_filter(prop, field, label, operator, klass)
                filters.append((name, filter_))
        return filters

    @classmethod
    def make_filter(mcs, prop, field, label, operator, klass):
        opts = klass.opts
        if operator.multiple:
            field = opts.list_class(field)
        return Filter(field, prop.key, label=label, operator=operator)

class FilterSet(six.with_metaclass(FilterSetMeta, object)):
    """

    Example usage:

    .. code-block:: python

        from models import Album, session
        from webargs.flaskparser import parser
        from filteralchemy import FilterSet

        class AlbumFilterSet(FilterSet):
            class Meta:
                model = Album
                query = session.query(Album)
                parser = parser

        query = AlbumFilterSet().filter()

    :param query: Optional SQLAlchemy query; if not provided, use query
        defined on options class
    """

    class Meta:
        """
        Available options:

        - `model`: SQLAlchemy model class
        - `query`: Query on `model`
        - `fields`: Sequence of model field names to include, or a callable that
        accepts a `FilterSet` subclass and returns a sequence of fields
        - `exclude`: Tuple or list of model field names to exclude, or a callable
        that accepts a `FilterSet` subclass and returns a sequence of fields
        - `list_class`: List field class; defaults to `List`
        - `converter`: `ModelConverter` instance; defaults to `ModelConverter()`
        - `operators`: Tuple or list of `Operator` classes
        - `default_operator`: Default operator; non-default operators will include
          operator labels in auto-generated filter names
        - `formatter`: Callable for building names of auto-generated filters
        - `column_overrides`: Dictionary mapping column names to operator and
          field overrides
        - `parser`: Webargs request parser
        """
        pass

    def __init__(self, query=None):
        self.query = query

    def filter(self):
        """Generate a filtered query from request parameters.

        :returns: Filtered SQLALchemy query
        """
        argmap = {
            filter.label or label: filter.field
            for label, filter in self.filters.items()
        }
        args = self.opts.parser.parse(argmap)
        query = self.query if self.query is not None else self.opts.query
        for label, filter in self.filters.items():
            value = args.get(filter.label or label)
            if value is not None:
                query = filter.filter(query, self.opts.model, label, value)
        return query
