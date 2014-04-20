import signal

from pyutils import *
from pyutils.network_utils import get_ip_address


def run_etcd_service(etcd, service, addr, run_server, attr=None):
    """
    addr format:
        127.0.0.1:80
        tcp://127.0.0.1:80
    """
    if addr.find('://')>=0:
        addr = addr.split('://', 1)[1]

    if attr is None:
        attr = {}

    host, port = addr.split(':')
    if host in ['0.0.0.0', '127.0.0.1']:
        host = get_ip_address() or host

    addr = ':'.join([host, port])

    def cleanup():
        WARN("warm shutdown service: %s %s" % (service, addr))
        etcd.unregister_service(service, addr)

    def trap(*args):
        sys.exit(0)

    try:
        etcd.register_service(service, addr, attr)
        signal.signal(signal.SIGINT, trap)
        signal.signal(signal.SIGTERM, trap)
        run_server()
    finally:
        cleanup()

#TODO remove
'''
def create_etcd_service_client(addr, attr, create_client=None):
    DEBUG("etcd_service_client: %s %s" % (addr, attr))
    if create_client:
        c = create_client(addr, attr)
    else:
        import zerorpc
        c = zerorpc.Client('tcp://'+addr)
    return c

def get_etcd_service(etcd, service, create_client=None):
    r = etcd.find_service(service)
    if r is None:
        return None

    addr, attr = r
    return create_etcd_service_client(addr, attr, create_client)

def stop_etcd_service(etcd, service):
    for s in etcd.find_service(service, find_one=False):
        c = create_etcd_service_client(s[0], s[1])
        raise Exception("TODO")
        #c._zerorpc_stop()
    return False

def remove_etcd_service(etcd, service, addr=None):
    return etcd.remove_service(service, addr)

'''
