# -*- coding: utf-8 -*-

class Operator(object):

    def filter(self, query, value):
        pass

class LookupOperator(Operator):

    lookup = None
    label = None
    multiple = False

    def filter(self, query, model, attr, value):
        column = getattr(model, attr)
        condition = getattr(column, self.lookup)(value)
        return query.filter(condition)

class Equal(LookupOperator):
    lookup = '__eq__'

class NotEqual(LookupOperator):
    lookup = '__ne__'
    label = 'ne'

class GreaterThan(LookupOperator):
    lookup = '__gt__'
    label = 'gt'

class GreaterEqual(LookupOperator):
    lookup = '__ge__'
    label = 'ge'

class LessThan(LookupOperator):
    lookup = '__lt__'
    label = 'lt'

class LessEqual(LookupOperator):
    lookup = '__le__'
    label = 'le'

class Like(LookupOperator):
    lookup = 'like'
    label = 'like'

class ILike(LookupOperator):
    lookup = 'ilike'
    label = 'ilike'

class In(LookupOperator):
    lookup = 'in_'
    label = 'in'
    multiple = True
