try:
    import json
except ImportError:
    import simplejson as json

import datetime

try:
    import numpy
except ImportError:
    numpy = None

DEFAULT_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

__all__ = ['dumps', 'loads']


class JSONDateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.strftime(DEFAULT_DATETIME_FORMAT)
        else:
            if numpy is not None:
                if isinstance(obj, numpy.ndarray):
                    return obj.tolist()
                elif isinstance(obj, (numpy.int64, numpy.int32)):
                    return int(obj)
                elif isinstance(obj, (numpy.float32, numpy.float64)):
                    return float(obj)
            else:
                return json.JSONEncoder.default(self, obj)

def datetime_decoder(d):
    if isinstance(d, list):
        pairs = enumerate(d)
    elif isinstance(d, dict):
        pairs = d.items()
    result = []
    for k,v in pairs:
        if isinstance(v, basestring):
            try:
                v = datetime.datetime.strptime(v, DEFAULT_DATETIME_FORMAT)
            except ValueError:
                try:
                    v = datetime.datetime.strptime(v, DEFAULT_DATE_FORMAT).date()
                except ValueError:
                    pass
        elif isinstance(v, (dict, list)):
            v = datetime_decoder(v)
        result.append((k, v))
    if isinstance(d, list):
        return [x[1] for x in result]
    elif isinstance(d, dict):
        return dict(result)

def dumps(obj, *args, **kwargs):
    if obj is None:
        return None
    return json.dumps(obj, cls=JSONDateTimeEncoder, *args, **kwargs)

def loads(s, *args, **kwargs):
    if not s:
        return None
    return json.loads(s, object_hook=datetime_decoder, *args, **kwargs)


def dump(obj, f):
    f.write(dumps(obj))

if __name__ == '__main__':
    mytimestamp = datetime.datetime.utcnow()
    mydate = datetime.date.today()
    data = dict(
        foo = 42,
        bar = [mytimestamp, mydate],
        date = mydate,
        timestamp = mytimestamp,
        struct = dict(
            date2 = mydate,
            timestamp2 = mytimestamp
        )
    )

    print repr(data)
    jsonstring = dumps(data)
    print jsonstring
    print repr(loads(jsonstring))

