# -*- coding: utf-8 -*-

class JsonApiFormatter(object):

    def __call__(self, field, operator):
        ret = 'filter[{}]'.format(field)
        if operator:
            ret += '[{}]'.format(operator)
        return ret

class DelimiterFormatter(object):

    def __init__(self, delimiter):
        self.delimiter = delimiter

    def __call__(self, field, operator):
        parts = [field]
        if operator:
            parts.append(operator)
        return self.delimiter.join(parts)

underscore_formatter = DelimiterFormatter('__')
