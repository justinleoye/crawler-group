from pyutils import *
from ..job_plugin import JobPlugin

class InheritPlugin(JobPlugin):
    def accept(self, job):
        return bool(job.get('inherit'))

    def on_start(self, job):
        inherit = job['inherit']
        base = self.worker.get_job(inherit)
        if base is None:
            raise Exception("invalid base job for inherit, not base job named %s found" % inherit)
        job.inherit_from(base)


