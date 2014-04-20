from __future__ import absolute_import

import etcd

from pyutils import *

from .backend import Backend

class EtcdBackend(Backend):
    def __init__(self, *args, **kwargs):
        super(EtcdBackend, self).__init__(*args, **kwargs)
        parts = self.endpoint.split(':')
        host = parts[0]
        port = 4001
        if len(parts)>1:
            port = int(parts[1])
        self.etcd = etcd.Client(host=host, port=port)

    def delete(self, key, recursive=True):
        path = self.get_path(key)
        try:
            self.etcd.delete(path, recursive=recursive)
            return True
        except KeyError:
            return False

    def as_dict(self, key=None):
        key = self.get_path(key)
        r = {}

        try:
            values = self.etcd.get(key).children
        except KeyError, e:
            return r

        DEBUG_(values)
        for x in values:
            k = self.path_to_key(x.key)
            if x.dir:
                r[k[-1]] = self.as_dict(k)
            else:
                r[k[-1]] = self.loads(x.value)
        return r

    def sub_items(self, key):
        key = self.get_path(key)

        try:
            values = self.etcd.get(key).children
        except KeyError, e:
            return

        if not values:
            return
        for x in values:
            k = self.path_to_key(x.key)
            if x.key != key:
                yield k[-1], self.loads(x.value)

    def list_items(self, key=None, recursive=True):
        key = self.get_path(key)

        try:
            values = self.etcd.get(key).children
        except KeyError, e:
            return

        DEBUG_(values)
        for x in values:
            k = self.path_to_key(x.key)
            if x.dir and recursive:
                for y in self.list_items(k, recursive):
                    yield y
            else:
                yield self.get_str_key(k), x.value
            
    def path_to_key(self, key):
        p = self.get_path(None)
        if key.startswith(p):
            key = key[len(p):]
        return key.lstrip('/').split('/')

    def get_path(self, key):
        key = self.get_key(key)
        return '/' + '/'.join(self.root + key)

    def _get(self, key):
        key = self.get_path(key)
        r = self.etcd.get(key).value
        return r

    def _set(self, key, value, ttl=None):
        key = self.get_path(key)
        return self.etcd.set(key, value, ttl=ttl)


