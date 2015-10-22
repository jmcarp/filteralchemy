# -*- coding: utf-8 -*-

from filteralchemy import operators

class Filter(object):
    """Base filter.

    :param Field field: Field to deserialize filter parameter
    :param str attr: Model attribute name
    :param str label: Lookup key on input dictionary
    :param operator: Operator or filter callable
    """
    def __init__(self, field=None, attr=None, label=None, operator=operators.Equal):
        self.field = field
        self.attr = attr
        self.label = label
        self.operator = operator

    def filter(self, query, model, attr, value):
        operator = self.operator() if isinstance(self.operator, type) else self.operator
        return operator(query, model, self.attr or attr, value)
