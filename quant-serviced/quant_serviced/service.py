import yaml
import zerorpc

from pyutils import *
from pyutils import dict_utils

from .context import serviced

#abstract service
class QuantService(object):
    def __init__(self, name):
        self.create_service(name)
        self._methods = None

    def create_service(self, name):
        self.client, self.config = serviced.get_service_client_and_config(name)

    @property
    def type(self):
        return self.config['type']

    @property
    def name(self):
        return self.config['name']

    @property
    def methods(self):
        if self._methods is None:
            self._methods = self.get_methods()
        return self._methods

    def __call__(self, method, *args):
        return self.client(method, *args)

    def get_methods(self):
        if self.type == 'zerorpc':
            d = self.client._zerorpc_inspect()
            for k,v in d['methods'].items():
                v['name'] = k
                if v.get('args'):
                    v['args'] = v['args'][1:]
                v['service'] = self.name
                try:
                    v['config'] = yaml.load(v['doc'])
                except:
                    v['config'] = {}
                    
            return d['methods']
        elif self.type == 'http':
            return {}
        else:
            raise NotImplementedError()

