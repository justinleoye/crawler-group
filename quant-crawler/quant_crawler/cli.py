import os
import yaml
import compago

import werkzeug.serving
import zerorpc

from pyutils import *
from pyutils.env_utils import Env

from quant_serviced import serviced
from quant_crawler.server import CrawlerServer
from quant_executor.utils import load_job_config_from_packages


app = compago.Application()
env = Env('QUANT_CRAWLER')

crawler_endpoint = env.get('endpoint', 'tcp://0.0.0.0:21130')

@app.command
def server(bind=None):
    e = bind or crawler_endpoint
    conf = {
        'endpoint': e,
    }
    s = CrawlerServer(conf)

    server = zerorpc.Server(s)
    INFO("bind to %s" % e)
    server.bind(e)
    try:
        attr = {
            'type': 'zerorpc',
            'module': 'quant_crawler'
        }
        serviced.run_service('quant_crawler', e, server.run, attr)
    except KeyboardInterrupt:
        INFO("warm shutdown")

@app.command
def crawl(mod, job):
    jobs = load_job_config_from_packages(['quant_crawler', mod])

def main():
    app.run()


