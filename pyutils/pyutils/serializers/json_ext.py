import yaml
import json
import datetime
import time
import types
from collections import Sequence, Mapping, Set

try:
    import bson
    import bson.objectid
except:
    bson = None
    INFO("bson not found")

from json import loads
import json

def encode(obj):
    if isinstance(obj, bytearray):
        return { '$binary': repr(obj)[1:-1] }

    elif isinstance(obj, str):
        try:
            s = obj.decode('utf8')
        except:
            s = { '$binary': repr(obj)[1:-1] }
        return s

    elif isinstance(obj, (str, unicode, int, float, bool, types.NoneType)):
        return obj

    elif hasattr(obj, 'as_json') and hasattr(obj.as_json, '__call__'):
        return encode(obj.as_json())

    elif bson is not None and isinstance(obj, bson.objectid.ObjectId):
        return str(obj)

    elif isinstance(obj, Sequence):
        return [encode(x) for x in obj]

    elif isinstance(obj, Mapping):
        return {k: encode(v) for k,v in obj.iteritems()}

    elif isinstance(obj, Set):
        return [encode(x) for x in obj]

    elif isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')

    elif isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d')

    elif isinstance(obj, datetime.time):
         return obj.strftime('%H:%M:%S')

    elif hasattr(obj, 'timetuple'):
        return int(time.mktime(obj.timetuple())) * 1000

    elif hasattr(obj, '__float__'):
        return float(obj)

    elif hasattr(obj, '__int__'):
        return int(obj)

    elif type(obj) is types.GeneratorType:
        return [encode(x) for x in obj]

    elif hasattr(obj, '__getstate__'):
        return encode(obj.__getstate__())

    else:
        try:
            return dict(obj)
        except:
            try:
                return list(obj)
            except:
                return str(obj)


def dumps(x):
    return json.dumps(encode(x), ensure_ascii=False)

