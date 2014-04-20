from __future__ import absolute_import

import types
import yaml

def loads(s):
    return yaml.load(s)

def dumps(x):
    if type(x) is types.GeneratorType:
        x = list(x)
    return yaml.dump(x)


