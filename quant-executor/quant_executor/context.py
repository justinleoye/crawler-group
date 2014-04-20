import yaml

from pyutils import *
from pyutils.env_utils import Env
from pyutils.create_obj import create_obj_from_config

from quant_etcd import context as etcd_context
from quant_executor.worker import Worker

env = Env('quant_executor')

_worker = None
_state_saver = None

etcd = etcd_context.get_etcd()

def get_worker():
    global _worker
    if _worker is None:
        config = etcd.as_dict('quant_executor')
        DEBUG("[create worker]")
        DEBUG("\n"+yaml.safe_dump(config))
        _worker = Worker(config)
    return _worker

def get_state_saver():
    global _state_saver
    if _state_saver is None:
        d = etcd['quant_executor/executor/state_saver']
        if d is None:
            return None
        _state_saver = create_obj_from_config(d)
    return _state_saver

def import_job_config(conf, depth=2):
    etcd.import_from_dict(conf, depth=depth, root='quant_executor')

def import_jobs(jobs):
    etcd = get_etcd()
    etcd.import_from_dict(jobs, root='quant_executor/jobs', depth=1)

