import random
import gevent

from pyutils import *
from pyutils import serialize_utils, yaml_utils
from pyutils.config_utils import load_config
from pyutils.network_utils import get_ip_address

class Backend(object):
    def __init__(self, endpoint=None, key_sep='.', root=None, serializer='yaml'):
        """
        root is used for etcd
        """

        self.endpoint = endpoint
        self.key_sep = key_sep

        root = self.get_key(root)
        self.root = root
        self.serializer = serialize_utils.get_serializer(serializer)

    def loads(self, s):
        return self.serializer.loads(s)

    def dumps(self, x):
        return self.serializer.dumps(x)

    def get_str_key(self, key):
        if isinstance(key, basestring):
            return key
        else:
            return self.key_sep.join(key)

    def get_key(self, key):
        if key is None:
            return []
        elif isinstance(key, (list,tuple)):
            return key
        elif isinstance(key, basestring):
            return key.split(self.key_sep)
        else:
            raise Exception("invalid key: %s" % key)

    def import_from_dict(self, conf, root=None, depth=None, ttl=None):
        if depth is not None:
            if depth <= 0:
                return
            new_depth = depth-1
        else:
            new_depth = depth

        if root is None:
            root = []
        elif not isinstance(root, (list,tuple)):
            root = self.get_key(root)

        if isinstance(conf, dict):
            for k,v in conf.items():
                key = root + [k]
                if (depth is None or depth>1) and isinstance(v, dict) and not '__etcd_leaf__' in v:
                    self.import_from_dict(v, key, depth=new_depth, ttl=ttl)
                else:
                    if '__etcd_leaf__' in v:
                        del v['__etcd_leaf__']
                    self.set(key, v, ttl=ttl)
        else:
            raise Exception("conf should be a dict: %s" % conf)

    def import_from_yaml(self, filename, **kwargs):
        config = load_config(filename, as_dict=True)
        self.import_from_dict(config, **kwargs)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def get(self, key, default=None):
        try:
            value = self._get(key)
        except KeyError, e:
            return default
        if value is None:
            return default
        return self.loads(value)

    def set(self, key, value, ttl=None):
        return self._set(key, self.dumps(value), ttl=ttl)

    def delete(self, key):
        raise NotImplementedError()

    def clear(self):
        self.delete(None)

    def get_service_key(self, service, addr=None):
        a = ['quant_etcd', 'services']
        if service:
            a.append(service)
        if addr:
            a.append(addr)
        return a

    """
    simple service discovery api
    """
    #TODO heartbeat, cf discoverd
    def register_service(self, service, addr, attr=None):
        INFO("quant_etcd.register_service %s %s\nattrs:\n%s" % (service, addr, yaml_utils.dump_clean(attr)))
        k = self.get_service_key(service, addr)
        self.set(k, attr)

    def unregister_service(self, service, addr):
        INFO("quant_etcd.unregister_service %s %s" % (service, addr))
        k = self.get_service_key(service, addr)
        self.delete(k)

    def remove_service(self, service, addr=None):
        INFO("quant_etcd.remove_service %s %s" % (service, addr))
        if service is None and addr is not None:
            for k,v in self.find_services().items():
                for a in v:
                    if a[0].startswith(addr+':'):
                        self.remove_service(k,a[0])
        else:
            k = self.get_service_key(service, addr)
            return self.delete(k)

    def find_service(self, service, find_one=True, host_list=None, wait=True):
        """
        if find_one returns (addr, attr) else returns [(addr, attr)]
        host_list is host priority if multi-host provide the same service
        """
        if wait:
            n = 0
            while True:
                r = self.find_service(service, find_one, host_list, wait=False)
                if r:
                    return r
                gevent.sleep(0.2)
                n += 1
                if n>10:
                    raise Exception("find_service wait timeout")

        k = self.get_service_key(service)
        addrs = list(self.sub_items(k))
        if find_one:
            if not addrs:
                return None
            s = None
            if host_list:
                for host in host_list:
                    for i in range(len(addrs)):
                        h = addrs[i][0].split(':')[0]
                        if h==host:
                            s = i
                            break
                    if s is not None:
                        break
            if s is None:
                s = random.randrange(len(addrs))
            return addrs[s]
        else:
            return addrs

    def find_services(self, wait=False):
        sk = self.get_service_key(None)
        r = {}
        for s,v in self.sub_items(sk):
            r[s] = self.find_service(s, find_one=False, wait=wait)
        return r


