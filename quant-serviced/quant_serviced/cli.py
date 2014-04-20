import os
import yaml
import compago
import zerorpc

from pyutils import *
from pyutils.env_utils import Env

from quant_serviced import serviced
from quant_serviced.server import QuantServiceD

app = compago.Application()
env = Env('QUANT_SERVICED')
serviced_endpoint = env.get('endpoint', 'tcp://0.0.0.0:21200')

@app.command
def server(bind=None):
    e = bind or serviced_endpoint
    config = {
        'endpoint': e
    }
    s = QuantServiceD(config)
    server = zerorpc.Server(s)
    INFO("bind to %s" % e)
    server.bind(e)
    try:
        serviced.run_service('quant_serviced', e, server.run)
    except KeyboardInterrupt:
        INFO("warm shutdown")

@app.command
def list():
    for k,v in serviced.list_services().items():
        print '[%s]' % k
        for a in v:
            print '    %s %s' % (a[0], a[1])
    print '-'*10

@app.command
def remove(service=None, addr=None):
    serviced.remove_service(service, addr)

def main():
    app.run()


