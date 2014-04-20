
from pyutils.msgpack_utils import packb, unpackb

def loads(s):
    return unpackb(s)

def dumps(x):
    return packb(x)

