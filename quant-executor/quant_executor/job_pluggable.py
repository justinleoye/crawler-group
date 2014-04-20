
from pyutils import *
from pyutils.create_obj import create_obj_from_config

from .utils import debug

class JobPluggableMixin(object):
    def init_plugins(self, plugin_confs, context=None):
        self.job_plugins = []
        if not plugin_confs:
            return

        if context is None:
            context = globals()

        for p in plugin_confs:
            kwargs = { 'worker': self }
            x = create_obj_from_config(p, kwargs=kwargs)
            self.job_plugins.append(x)

    def call_job_plugin(self, job, meth, result=None):
        for p in self.job_plugins:
            if p.accept(job):
                if debug.active:
                    DEBUG_("run plugin %s.%s" % (p.__class__.__name__, meth))
                f = getattr(p, meth)
                if f is None:
                    continue

                if meth in ['done', 'fail']:
                    r = f(job, result)
                else:
                    r = f(job)

                if r==False:
                    if debug.active:
                        DEBUG("skip other plugins %s" % meth)
                    return False
        return True

