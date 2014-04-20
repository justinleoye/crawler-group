from __future__ import absolute_import
import imp
from .type_utils import *
from .log_utils import *

try:
    from importlib import import_module
except:
    #fix for stdandard __import__
    #http://stackoverflow.com/questions/211100/pythons-import-doesnt-work-as-expected
    def import_module(name):
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod

def import_modules(modules, env=None):
    if env is None:
        env = {}
    if is_str(modules):
        modules = [modules]

    if not modules:
        return env

    for mod in modules:
        #exec('from %s import *' % mod, env)
        m = import_module(mod)
        if hasattr(m, '__all__'):
            d = m.__all__
        else:
            d = m.__dict__.keys()
        DEBUG_('env for mod %s: %s' % (mod, d))
        for k in d:
            env[k] = m.__dict__[k]
    DEBUG_('env from %s: %s' % (modules, env.keys()))
    return env

def import_module_from_code(code, module_name=None):
    if module_name is None:
        module_name = 'my_module_from_code'
    mod = imp.new_module(module_name)
    exec code in mod.__dict__
    return mod

