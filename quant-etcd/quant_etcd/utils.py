import os

from .backends.yaml import YamlBackend
from .backends.etcd import EtcdBackend

def create_etcd(endpoint=None, **kwargs):
    if endpoint is None:
        endpoint = os.environ.get('QUANT_ETCD_ENDPOINT')

    if not endpoint:
        raise Exception("endpoint needed (env: QUANT_ETCD_ENDPOINT)")

    parts = endpoint.split('://')
    if not parts:
        raise Exception("invalid ETCD endpoint: %s" % endpoint)
    elif len(parts)==1:
        backend = 'etcd'
        endpoint = parts[0]
    else:
        backend = parts[0]
        endpoint = parts[1]

    if backend in ['etcd', 'http', 'tcp']:
        return EtcdBackend(endpoint, **kwargs)
    elif backend=='yaml':
        return YamlBackend(endpoint, **kwargs)
    else:
        raise Exception("invalid ETCD endpoint: %s" % endpoint)


