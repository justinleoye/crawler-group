import sys
import gevent

from pyutils.debug_utils import *
from pyutils.import_utils import *
from pyutils.config_utils import *
from pyutils.create_obj import create_obj_from_config

from .job_pluggable import JobPluggableMixin
from .job import Job

from .utils import *

class Worker(JobPluggableMixin):
    def __init__(self, config={}):
        DEBUG('quant_executor.Worker: %s' % yaml.dump(config))
        self.set_config(config)
        self.init_plugins(self.config.get('job_plugins'))

    def set_config(self, config):
        self.config = config
        for k,j in self.config['jobs'].items():
            if not 'name' in j:
                j['name'] = k
            
    def job_type_conf(self, t):
        return self.config['job_types'].get(t, {})

    def get_executor(self, job):
        executor = job.get('executor')
        t = job.get('type')
        if executor is None:
            executor = self.job_type_conf(t).get('executor')
        DEBUG('type: %s executor: %s' % (t, executor))
        return create_obj_from_config(executor)

    def transform(self, jobs):
        if not isinstance(jobs, list):
            jobs = [jobs]

        for t in self.transformers:
            new_jobs = []
            for j in jobs:
                x = t.transform(j)
                if isinstance(x, (dict, basestring)):
                    new_jobs.append(x)
                else:
                    for y in x:
                        new_jobs.append(y)
            jobs = new_jobs
        return jobs

    def get_job(self, job):
        if isinstance(job, basestring):
            job = self.config['jobs'].get(job)

        if isinstance(job, dict):
            job = Job(job)
        else:
            raise Exception("invalide job: %s" % job)
        return job

    def get_jobs(self):
        return self.config['jobs']

    def job_done(self, job, r=None, check_run=False):
        self.call_job_plugin(job, 'on_done', r)

    def job_fail(self, job, e=None):
        self.call_job_plugin(job, 'on_fail', e)

    def run_job(self, job, debug_info=True):
        if debug_info:
            DEBUG("run job: %s" % job)

        job = self.get_job(job)
        r = None
        if self.call_job_plugin(job, 'on_start')!=False:
            if debug_info:
                DEBUG("expanded job after plugin:\n%s" % job.repr_yaml())
            try:
                executor = self.get_executor(job)
                r = executor(job)
            except Exception, e:
                self.job_fail(job, e)
                raise
        self.job_done(job, r)
        return r

    def start_job(self, job, debug_info=True):
        gevent.spawn(self.run_job, job, debug_info)
        return True

