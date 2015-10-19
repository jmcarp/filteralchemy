# -*- coding: utf-8 -*-

class Operator(object):

    lookup = None
    label = None
    multiple = False

    def __call__(self, query, model, attr, value):
        column = getattr(model, attr)
        condition = getattr(column, self.lookup)(value)
        return query.filter(condition)

class Equal(Operator):
    lookup = '__eq__'
    label = 'eq'

class NotEqual(Operator):
    lookup = '__ne__'
    label = 'ne'

class GreaterThan(Operator):
    lookup = '__gt__'
    label = 'gt'

class GreaterEqual(Operator):
    lookup = '__ge__'
    label = 'ge'

class LessThan(Operator):
    lookup = '__lt__'
    label = 'lt'

class LessEqual(Operator):
    lookup = '__le__'
    label = 'le'

class Like(Operator):
    lookup = 'like'
    label = 'like'

class ILike(Operator):
    lookup = 'ilike'
    label = 'ilike'

class In(Operator):
    lookup = 'in_'
    label = 'in'
    multiple = True
