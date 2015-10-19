# -*- coding: utf-8 -*-

from filteralchemy import operators

class Filter(object):

    def __init__(self, attr=None, field=None, label=None, operator=operators.Equal):
        self.attr = attr
        self.field = field
        self.label = label
        self.operator = operator

    def filter(self, query, model, value):
        operator = self.operator() if isinstance(self.operator, type) else self.operator
        return operator(query, model, self.attr, value)
