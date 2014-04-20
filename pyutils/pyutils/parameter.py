#import jsonschema

import yaml
import json

from pyutils.log_utils import *
from pyutils.datetime_utils import str_to_datetime

class Parameter(dict):
    """
    params:
        period: 
            #type is infered from default
            #if default is null, then params MUST be provided

            #inherite from param template `period`
            template: period

        time_field: 
            default: time
    """

    templates = {}

    @classmethod
    def register_templates(cls, templates):
        cls.templates.update(templates)

    def __init__(self, conf):
        d = {}
        if conf:
            t = conf.get('template')
            if t is not None:
                d = Parameter.templates.get(t, {})
            d.update(conf)
        super(Parameter, self).__init__(d)
        self.validate()

    def get_type_of(self, v):
        if isinstance(v, (str, unicode)):
            return 'string'
        elif isinstance(v, (int, long)):
            return 'integer'
        elif isinstance(v, bool):
            return 'boolean'
        elif isinstance(v, float):
            return 'number'
        elif isinstance(v, (list,tuple)):
            return 'array'
        elif isinstance(v, dict):
            return 'object'
        elif v is None:
            raise Exception("cannot infer params type for None")
        else:
            raise Exception("unknown type for class: %s" % v.__class__.__name__)

    def validate(self):
        if not 'type' in self and 'default' in self:
            self['type'] = self.get_type_of(self['default'])
        if not 'title' in self:
            self['title'] = self.get('name')

    @property
    def default(self):
        if 'default' in self:
            return self['default']
        else:
            raise Exception("No default value provided for %s" % self.name)
    
    @property
    def name(self):
        return self['name']

    @property
    def type(self):
        if 'type' in self:
            return self['type']
        else:
            raise Exception("unknown type and no default value")

    def coerce(self, value):
        type = self.type
        if type!='string' and isinstance(value, (str,unicode)):
            DEBUG_('%s %s' % (type, value))
            if type=='datetime':
                value = str_to_datetime(value)
            else:
                value = json.loads(value)
        return value

    def value(self, params):
        k = self.name
        if k in params:
            v = self.coerce(params[k])
        else:
            v = self.default
        return v

class Parameters(dict):
    def __init__(self, conf):
        p = {}
        if conf:
            for k,v in conf.iteritems():
                if not 'name' in v:
                    v['name'] = k
                p[k] = Parameter(v)
        super(Parameters, self).__init__(p)

    def validate_params(self, params):
        #TODO
        #validate with jsonschema
        #name field?
        return True

    def values(self, params, strict=False):
        if strict:
            r = {}
        else:
            r = dict(params)

        for k,p in self.iteritems():
            r[p.name] = p.value(params)
        return r

    def as_json(self):
        return {k: dict(v) for k,v in self.iteritems()}


def get_params(spec, params):
    if not spec:
        return dict(params)
    parameters = Parameters(spec)
    if not parameters.validate_params(params):
        raise Exception("params error: expect %s got %s" % (parameters, params))
    return parameters.values(params)

