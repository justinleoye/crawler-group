
from pyutils import *
from pyutils.env_utils import Env

from .utils import create_etcd

env = Env('QUANT_ETCD')
_etcd = None
_local_etcd = None

def get_etcd():
    global _etcd
    if _etcd is None:
        e = env.get('endpoint', 'etcd://127.0.0.1:4001')
        _etcd = create_etcd(e, root=None, key_sep='/')
    return _etcd

def get_local_etcd():
    global _local_etcd
    if _local_etcd is None:
        e = env.get('endpoint_local')
        if e is None:
            return None
        _local_etcd = create_etcd(e, root=None, key_sep='/')
    return _local_etcd

def get_etcd_list():
    r = []
    for f in [get_etcd, get_local_etcd]:
        e = f()
        if e is not None:
            r.append(e)
    return r

