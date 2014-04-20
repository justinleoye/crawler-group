import os
import yaml
import compago

from pyutils import *
from pyutils.env_utils import Env

from quant_serviced import serviced
from quant_executor import context
from quant_executor.worker import Worker
from quant_executor.utils import load_job_config_from_packages

app = compago.Application()

env = Env('quant_executor')

executor_endpoint = env.get('endpoint', 'tcp://0.0.0.0:21160')

@app.command
def start(job, package=None):
    if package is None:
        w = context.get_worker()
    else:
        config = load_job_config_from_packages(['quant_executor', package])
        w = Worker(config)
    r = w.run_job(job)
    print r

@app.command
def server(bind=None, job_modules=''):
    import zerorpc

    job_modules = ['quant_executor'] + job_modules.split(',')
    config = load_job_config_from_packages(job_modules)
    worker = Worker(config)
    s = zerorpc.Server(worker)
    e = bind or executor_endpoint

    INFO("quant_executor server bind to %s with job_modules: %s" % (bind, job_modules))

    s.bind(e)
    attr = {
        'type': 'zerorpc',
        'module': 'quant_executor'
    }
    serviced.run_service('quant_executor', e, s.run, attr)

@app.command
def import_job_config(package):
    c = load_job_config_from_package(package)
    context.import_job_config(c)
    

def main():
    app.run()


