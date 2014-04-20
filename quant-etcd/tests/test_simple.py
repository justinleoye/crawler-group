from quant_etcd import *

from pyutils.path_utils import rel_filename

def test_etcd():
    etcd = create_etcd('etcd://127.0.0.1:4001')
    f = rel_filename('test_conf.yml', __file__)
    print f
    etcd.import_from_yaml(f)
    print etcd.get('a.b.c')
    print etcd.get('a.e')
    print etcd.get('f')
    print etcd.get('a.g')
    
if __name__ == '__main__':
    test_etcd()


