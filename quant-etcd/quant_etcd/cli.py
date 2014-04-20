import os
import yaml
import compago

from pyutils import *
from pyutils.env_utils import Env

from quant_etcd import create_etcd, context


app = compago.Application()


@app.command
def import_yaml(filename, root=None, depth=2, clear=0):
    depth = int(depth)
    clear = int(clear)
    etcd = create_etcd(root=root)
    if clear==1:
        etcd.clear()
    etcd.import_from_yaml(filename, depth=depth)

@app.command
def dump(root=None):
    etcd = create_etcd(root=root, key_sep='/')
    d = etcd.as_dict()
    print yaml.safe_dump(d)

@app.command
def list_keys(root=None):
    etcd = create_etcd(root=root, key_sep='/')
    for x in etcd.list_items():
        print x[0], '=', x[1]

@app.command
def services():
    etcd = context.get_etcd()
    for k,v in etcd.find_services().items():
        print '[%s]' % k
        for a in v:
            print '    %s %s' % (a[0], a[1])
    print '-'*10

@app.command
def remove_service(service):
    etcd = context.get_etcd()
    etcd.remove_service(service)


def main():
    app.run()

