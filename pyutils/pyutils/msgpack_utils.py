import msgpack
from datetime import datetime

"""
packed_dict = msgpack.packb(useful_dict, default=encode_datetime)
this_dict_again = msgpack.unpackb(packed_dict, object_hook=decode_datetime)
"""


DATETIME_FMT = "%Y-%m-%dT%H:%M:%S.%f"

def decode_obj(obj):
    t = obj.get('__type__')
    if t is not None:
        s = obj.get('__repr__')
        if t=='datetime':
            obj = datetime.strptime(s, DATETIME_FMT)
    return obj

def encode_obj(obj):
    if isinstance(obj, datetime):
        return {
            '__type__': 'datetime',
            '__repr__': obj.strftime(DATETIME_FMT)
        }
    return obj

def unpackb(value):
    return msgpack.unpackb(value, object_hook=decode_obj)

def packb(value):
    return msgpack.packb(value, default=encode_obj)
