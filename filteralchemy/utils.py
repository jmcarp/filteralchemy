# -*- coding: utf-8 -*-

import functools

import sqlalchemy as sa

def _index_columns(engine, klass):
    model = klass.opts.model
    inspector = sa.inspect(engine)
    indexes = inspector.get_indexes(model.__tablename__)
    return {index['column_names'][0] for index in indexes}

def index_columns(engine):
    return functools.partial(_index_columns, engine)
