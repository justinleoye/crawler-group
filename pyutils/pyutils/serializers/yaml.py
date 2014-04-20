from __future__ import absolute_import

import yaml

def loads(s):
    if s is None:
        return None
    return yaml.load(s)

def dumps(x):
    return yaml.dump(x)


