# -*- coding: utf-8 -*-

class JsonApiFormatter(object):

    def __call__(self, label, operator):
        ret = 'filter[{}]'.format(label)
        if operator.label:
            ret += '[{}]'.format(operator.label)
        return ret

class DelimiterFormatter(object):

    def __init__(self, delimiter):
        self.delimiter = delimiter

    def __call__(self, label, operator):
        parts = [label]
        if operator.label:
            parts.append(operator.label)
        return self.delimiter.join(parts)

underscore_formatter = DelimiterFormatter('__')
