from pyutils import *
from pyutils import config_utils, dict_utils, network_utils

from quant_etcd.context import get_etcd_list
from quant_etcd.service import run_etcd_service

from .utils import QUANT_SERVICED_DEV

class QuantServiceD(object):
    def __init__(self, config=None):
        if config is None:
            config = {}
        self.config = config

    #TODO cache
    def get_service_client(self, service, create_client=None, raise_error_for_none=True):
        r = self.get_service_config(service)
        if r is None:
            if raise_error_for_none:
                raise Exception("service not exists: %s" % service)
            else:
                return None
        addr, attr = r
        return self.create_service_client(addr, attr, create_client)

    def get_service_client_and_config(self, service, create_client=None):
        r = self.get_service_config(service)
        if r is None:
            return None
        addr, attr = r
        client = self.create_service_client(addr, attr, create_client)
        return client, attr

    def get_service_config(self, service):
        for e in get_etcd_list():
            host_list = None
            if QUANT_SERVICED_DEV:
                host_list = [network_utils.get_ip_address()]
            r = e.find_service(service, host_list=host_list)
            if r is not None:
                addr, attr = r
                if attr is None:
                    attr = {}
                dict_utils.set_dict_defaults(attr, type='zerorpc', name=service)
                return addr, attr
    
    def create_service_client(self, addr, attr, create_client=None):
        DEBUG("create_service_client: %s %s" % (addr, attr))
        if create_client:
            c = create_client(addr, attr)
        else:
            t = attr.get('type', 'zerorpc')
            if t=='zerorpc':
                import zerorpc
                c = zerorpc.Client('tcp://'+addr)
            elif t=='http':
                #TODO
                c = None
            else:
                c = None
        return c

    def run_service(self, service, addr, run_server, attr):
        if attr:
            if not 'name' in attr:
                attr['name'] = service

            if attr.get('module'):
                pc = config_utils.load_config_from_package(attr['module'], 'config/service.yml')
                if pc:
                    d = pc['services'].get(service, {})
                    attr = dict_utils.extend(d, attr)

        for e in get_etcd_list():
            r = run_etcd_service(e, service, addr, run_server, attr)
            return r

    def list_services(self):
        r = {}
        for e in get_etcd_list():
            for k,v in e.find_services().items():
                if not v:
                    continue
                if not k in r:
                    r[k] = []
                r[k] += v
        return r

    def stop_service(self, service):
        for e in get_etcd_list():
            r = e.stop_service(service)
            if r:
                return r
        return False

    def remove_service(self, service, addr):
        for e in get_etcd_list():
            e.remove_service(service, addr)
            break
        

