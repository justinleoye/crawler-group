import yaml
import gevent
import string
from datetime import datetime, date, time

import jinja2
import jsonize

from pyutils import *
import pyutils.parameter

from quant_serviced import serviced
from pyutils.datetime_utils import get_date_range, date_sequence

from quant_executor.job import Job
from quant_executor.job_plugin import JobPlugin

class TemplatePlugin(JobPlugin):
    def init(self, default_params=None):
        env = jinja2.Environment()
        env.finalize = self.finalize
        glb = {
            'date': date,
            'datetime': datetime,
            'time': time,
            'env': lambda x: os.environ.get(x)
        }
        env.globals.update(glb)

        filters = {
            'tojson': jsonize.dumps_simple
        }
        env.filters.update(filters)

        self.env = env

        self.default_params = default_params or {}

    def finalize(self, v):
        if v is None or isinstance(v, jinja2.Undefined):
            return 'null'
        return v

    def render_template(self, t, params, as_dict=True):
        d = dict(self.default_params)
        d.update(params)
        r = self.env.from_string(t).render(d)
        if as_dict:
            r = yaml.load(r)
        return r

    def normalize_value(self, key, value):
        if key=='symbol':
            #TODO quant_data env switch
            #NOTE: sorted, is for `order by time,symbol` in realtime pipeline
            quant_data = serviced.get_service_client('quant_data.stock')
            return sorted(quant_data.get_symbols(value))
        elif key=='period':
            if value=='*':
                return 'm1 m5 m30 day week month quarter year'.split()
        elif key=='date':
            if is_str(value):
                d0, d1 = get_date_range(value)
                return list(date_sequence(d0, end_date=d1, to_str=True))
            elif isinstance(value, dict):
                return list(date_sequence(value.get('start'), end_date=value.get('end'), to_str=True))
        return get_list(value)

    def generate_multi_params(self, p):
        if is_list(p):
            for x in p:
                yield x
        elif is_dict(p):
            if not p:
                yield {}
                return

            k = p.keys()[0]
            d = dict(p)
            del d[k]

            for v in self.normalize_value(k, p[k]):
                for x in self.generate_multi_params(d):
                    x[k] = v
                    yield x
        else:
            raise Exception("not support params %s" % p)

    def get_params(self, params):
        if is_str(params):
            params = self.render_template(params, {})
        return params

    def template_params(self, job):
        params = job.get('params')
        params_multi = job.get('params_multi')
        if params:
            yield self.get_params(params)
        elif params_multi:
            params_multi = self.get_params(params_multi)
            for p in self.generate_multi_params(params_multi):
                yield p
        else:
            yield {}

    def template_jobs(self, job):
        template_job = self.worker.get_job(job['template'])
        params_spec = template_job.get('params_spec')
        for params in self.template_params(job):
            params = pyutils.parameter.get_params(params_spec, params)
            #TODO params validate
            t = template_job['job_template']
            j = {
                'name': job['name'],
            }
            j.update(self.render_template(t, params))
            yield Job(j)

    def accept(self, job):
        return bool(job.get('template'))

    def on_done(self, job):
        #don't check depenency for template job
        return False
        
    def on_start(self, job):
        t = job['template']

        job.run()

        n = 0
        for j in self.template_jobs(job):
            while job.paused:
                gevent.sleep(1)

            if job.stopped:
                INFO("job is stopped")
                break

            #skip print debug info for large template jobs
            n += 1
            if n==10:
                WARN("NOTE: would not print start job msg any more for this template job: %s" % job.readable_id)

            j.forked_from(job)
            job.append_fork(j)

            jid = self.worker.run_job(j, debug_info=n<10)

            #NOTE! sleep for gevent switch (event sleep is 0)
            sleep = job.get('sleep') or 0
            gevent.sleep(sleep)

        self.worker.job_done(job, True, check_run=False)
        return False


