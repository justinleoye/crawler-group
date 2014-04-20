import json
import pickle
from pyutils import serializers

def get_serializer(s):
    if isinstance(s, basestring):
        if s=='json':
            return json
        elif s=='pickle':
            return pickle
        elif hasattr(serializers, s):
            m = getattr(serializers, s)
            return m
    elif hasattr(s, 'loads') and hasattr(s, 'dumps'):
        return s
    else:
        return None
    
def loads(s, format=None):
    x = get_serializer(format)
    if x is not None:
        return x.loads(x)
    else:
        return s

def dumps(x, format=None):
    x = get_serializer(format)
    if x is not None:
        return x.dumps(x)
    else:
        return str(x)

