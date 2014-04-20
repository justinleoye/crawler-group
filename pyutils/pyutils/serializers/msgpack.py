
from __future__ import absolute_import
import msgpack

def loads(s):
    return msgpack.unpack(s)

def dumps(x):
    return msgpack.pack(x)

