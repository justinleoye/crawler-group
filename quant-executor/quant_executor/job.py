import copy
from datetime import datetime
from collections import defaultdict
import jsonize

from pyutils import *
from pyutils import yaml_utils
from pyutils.dict_utils import recursive_merge

class Job(defaultdict):
    def __init__(self, *args, **kwargs):
        #allow create with: Job(None)
        if args==(None,):
            args = ()
        super(Job, self).__init__(None, *args, **kwargs)

    @property
    def name(self):
        return self.get('name')

    @property
    def status(self):
        return self.get('__status__')

    @property
    def serialize_id(self):
        if self.get('serialize_id') is not None:
            return self['serialize_id']
        return self.readable_id

    @property
    def readable_id(self):
        p = self.get('prefix') 
        g = self.get('group')
        n = self.get('name')
        if n is None:
            raise Exception("job name missing: %s" % self)

        if p is not None:
            s = p + n
        elif g is not None:
            s = g + '/' + n
        else:
            s = n
        t = self.get('tags')
        if t:
            if is_list(t):
                t = ':'.join(map(str,t))
            else:
                t = str(t)
            s += '/'+t
        return s
        
    def add_tags(self, tags):
        tags = get_list(tags)
        if not tags:
            return
        if self.get('tags') is None:
            self['tags'] = tags
        else:
            self['tags'] += tags

    def as_json(self):
        return dict(self)

    @classmethod
    def from_json(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def inherit_from(self, base):
        base = copy.deepcopy(base)
        r = recursive_merge(base, self)
        for k, v in r.iteritems():
            self[k] = v

        if 'inherit' in self:
            del self['inherit']

    def add_event_trigger(self, condition, event):
        if condition is None:
            for k,v in event.iteritems():
                self.add_event_trigger(k,v)
        else:
            et = self.get('event_trigger', {})
            es = get_list(et.get(condition, []))
            es.append(event)
            et[condition] = es
            self['event_trigger'] = et


    def repr_yaml(self):
        x = jsonize.encode_simple(self)
        return yaml_utils.dump_clean(x)


    """
    job status
    """

    def stop(self):
        self['__status__'] = 'stop'
        self['__stopped_at__'] = datetime.now()

    def pause(self):
        self['__last_status__'] = self['__status__']
        self['__status__'] = 'pause'
        self['__paused_at__'] = datetime.now()

    def cont(self):
        self['__status__'] = self['__last_status__']
        self['__continue_at__'] = datetime.now()

    def fail(self):
        self['__status__'] = 'fail'
        self['__fail_at__'] = datetime.now()

    def start(self):
        self['__status__'] = 'start'
        self['__start_at__'] = datetime.now()

    def run(self):
        self['__status__'] = 'run'
        self['__run_at__'] = datetime.now()

    def done(self):
        self['__status__'] = 'done'
        self['__done_at__'] = datetime.now()

    def schedule(self):
        self['__status__'] = 'schedule'
        self['__schedule_at__'] = datetime.now()

    def in_status(self, *args):
        return self.get('__status__') in args

    @property
    def active(self):
        return self.get('active')!=False

    @property
    def stopped(self):
        return self.get('__status__')=='stop'

    @property
    def paused(self):
        return self.get('__status__')=='pause'

    @property
    def started(self):
        return self.get('__status__')=='start'

    @property
    def finished(self):
        return self.get('__status__')=='done'

    @property
    def failed(self):
        return self.get('__status__')=='fail'

    @property
    def id(self):
        return self.get('id')

    @property
    def status(self):
        return self.get('__status__')

    """
    fork utils
    """

    def forked_jobs(self):
        return self.get('__forked_jobs__', [])

    def fork(self):
        j = copy.deepcopy(self)
        #remove meta info
        for k in j.keys():
            if k.startswith('__') and k.endswith('__'):
                del j[k]
        if 'id' in j:
            del j['id']
        if '_id' in j:
            del j['_id']
        j['__forked_from__'] = self.id
        return j

    def forked_from(self, job=None):
        if job is None:
            return self.get('__forked_from__')
        else:
            self['__forked_from__'] = job.get('id')
        return self

    def append_fork(self, job):
        if self.get('__forked_jobs__') is None:
            self['__forked_jobs__'] = []
        self['__forked_jobs__'].append(job.id)
        if not '__forked_from__' in job:
            job['__forked_from__'] = self.id
        return self

