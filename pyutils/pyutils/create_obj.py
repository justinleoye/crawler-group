import yaml
import sys
import re
import imp

from .func_utils import call_with_kwargs_filter
from .config_utils import *
from .import_utils import *
from .type_utils import *
from .log_utils import *
from .exception_utils import *

def load_variable(module_and_name, raise_exception=True):
    """Loads the module and returns the class.

    >>> loadclass('jsonpickle._samples.Thing')
    <class 'jsonpickle._samples.Thing'>

    >>> loadclass('example.module.does.not.exist.Missing')


    >>> loadclass('samples.MissingThing')
    """
    try:
        a = module_and_name.rsplit('.', 1)
        if len(a)==2:
            module, name = a
        else:
            module = a[0]
            name = None
        m = sys.modules.get(module)
        if m is not None:
            imp.reload(m)
        else:
            __import__(module)
        m = sys.modules[module]
        if name is not None:
            return getattr(m, name)
        else:
            return m
    except Exception, e:
        if raise_exception:
            raise
        ERROR(e)
        ERROR(TRACE_BACK())
        return None

load_class = load_variable
load_function = load_variable

def decode_args_value(value):
    #TODO sandboxing
    if isinstance(value, dict):
        if '__name__' in value and '__module__' in value:
            return load_variable(value['__module__'] + '.' + value['__name__'])
        elif '__obj__' in value:
            return create_obj_from_config(value['__obj__'])
    return value

def decode_args(args):
    if args is None:
        return None
    elif isinstance(args, list):
        return [decode_args_value(x) for x in args]
    else:
        return {k: decode_args_value(v) for k,v in args.iteritems()}

def create_obj_from_config(config, env=None, args=None, kwargs=None, evaluate=None):
    if config is None:
        raise Exception("create_obj_from_config config is None")

    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    if env is None:
        env = globals()

    if evaluate is None:
        if is_str(config) and re.match('^[a-zA-Z0-9_.]*$', config):
            evaluate = False
        else:
            evaluate = True

    if is_str(config):
        if evaluate:
            return eval(config, env)
        else:
            cls = config
            if cls.find('.')>=0:
                c = load_variable(cls)
            else:
                c = env.get(cls)
            if c is None:
                raise Exception("class %s not found in %s" % (cls, env.keys()))
            else:
                return call_with_kwargs_filter(c, decode_args(args), decode_args(kwargs))
    elif hasattr(config, 'get'):
        cls = config.get('class') or config.get('class_name')
        code = config.get('code') or config.get('source_code')
        module = config.get('module')
        if module and cls:
            cls = module + '.' + cls

        cls_pattern = config.get('class_pattern')

        if code is not None:
            #TODO: this is just a hack
            #general solution is use pyfile_utils.py
            #coding declare in web submitted code raise error 'encoding declaration in Unicode string'
            if isinstance(code, unicode):
                code = code.encode('utf8')

            mod = import_module_from_code(code)
            env = mod.__dict__
            
        if cls is None and cls_pattern is not None:
            p = re.compile(cls_pattern)
            for k,v in env.iteritems():
                if inspect.isclass(v) and p.match(k) is not None:
                    cls = v
                    break

        if cls is not None:
            args = config.get('args', args)

            #important! don't change kwargs
            #for example, if kwargs has default value {}
            #then change kwargs will change default value
            kwargs = dict(kwargs)
            kwargs.update(config.get('kwargs') or {})

            if cls.find('.')>=0:
                c = load_variable(cls)
                if c is None:
                    raise Exception("load variables %s failed" % cls)
            else:
                c = env.get(cls)
                if c is None:
                    raise Exception("class %s not found in %s" % (cls, env.keys()))
            try:
                obj = call_with_kwargs_filter(c, decode_args(args), decode_args(kwargs))
            except:
                ERROR("create_obj_from_config error, class: %s args: %s kwargs: %s" % (c.__name__, args, kwargs))
                raise
            return obj

        elif code is not None:
            attr = config.get('attribute')
            func = config.get('factory')
            if attr:
                return getattr(mod, attr)
            elif func:
                return getattr(mod, func)()
            else:
                return mod
        else:
            ERROR("create_obj_from_config returns None: %s" % config)
    else:
        return config

def create_env_with_import(conf, default=None):
    mod_path = conf.get('module_path')
    mod = conf.get('module')
    if mod_path:
        sys.path.append(mod_path)
    env = import_modules(mod, default)
    return env

def create_obj_with_import(conf, key=None, default_env=None, args=None, kwargs=None):
    """
    example1:
        conf:
            module: distributed_cep.publishers
            publisher: KeyValuePublisher('symbol')
        key: publisher
        args: []
        kwargs:
            master: self.master

    example2:
        conf:
            module: distributed_cep.publishers
            class: KeyValuePublisher
            args: ['symbol']
        key: None
    """
    env = create_env_with_import(conf, default_env)

    if key is None:
        obj = conf
    else:
        obj = conf.get(key)
        if obj is None:
            raise Exception("create_obj_with_import conf[%s] is None" % key)

    if not isinstance(obj, list):
        r = create_obj_from_config(obj, env, args=args, kwargs=kwargs)
    else:
        #create pipeline
        r = None
        for o in obj:
            x = create_obj_from_config(o, env, args=args, kwargs=kwargs)
            if r is None:
                r = x
            else:
                r = r | x
    return r


