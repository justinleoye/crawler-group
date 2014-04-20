import os
import pkg_resources
import yaml
import copy

from pyutils import *
from pyutils.dict_utils import recursive_merge
from pyutils.config_utils import load_config_from_package

debug = DebugInfo(active=os.environ.get('QUANT_EXECUTOR_DEBUG')=='1')

def load_job_config_from_package_recursive(p, loaded, configs):
    if p in loaded:
        return
    loaded[p] = True
    c = load_config_from_package(p, 'config/job.yml')
    INFO("load job config from package: %s\n%s" % (p, c))
    if not c:
        return
    if 'dependencies' in c:
        for d in c['dependencies']:
            load_job_config_from_package_recursive(d, loaded, configs)
    configs.append(c)

def merge_job_configs(configs):
    if not configs:
        return None

    c = copy.deepcopy(configs[0])
    for i in range(1, len(configs)):
        d = configs[i]
        recursive_merge(c, configs[i])
    return c


def load_job_config_from_packages(packages):
    configs = []
    loaded = {}
    for p in packages:
        if p is None:
            p = 'quant_executor'
        load_job_config_from_package_recursive(p, loaded, configs)

    return merge_job_configs(configs)

