import itertools
import re
from django.utils.module_loading import import_string


def get_function(path):
    """ Import a function by fqn """
    return import_string(path)


class ChoiceEnum(object):
    def __init__(self, choices):
        if isinstance(choices, basestring):
            choices = choices.split()
        if all([isinstance(choices, (list, tuple)),
                all(isinstance(x, tuple) and len(x) == 2 for x in choices)]):
            values = choices
        else:
            values = zip(itertools.count(1), choices)
        for v, n in values:
            name = re.sub('[- ]', '_', n.upper())
            setattr(self, name, v)
            if isinstance(v, str):
                setattr(self, v.upper(), v)
        self._choices = values

    def __getitem__(self, idx):
        return self._choices[idx]

    def getdisplay(self, key):
        return [v[1] for v in self._choices if v[0] == key][0]

    def deconstruct(self):
        """migration serializer"""
        path = "crowdsourcing.util.ChoiceEnum"
        args = (self._choices,)
        kwargs = {}
        return path, args, kwargs
