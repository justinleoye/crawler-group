import inspect
import types

from pyutils.log_utils import *
from pyutils.debug_utils import *
from pyutils.dict_utils import sub_dict

class BindFirstFunction(object):
    def __init__(self, f, *args, **kwargs):
        self.f = f
        self.args = list(args)
        self.kwargs = dict(kwargs)

    def __call__(self, *args, **kwargs):
        ags = list(self.args) + list(args)
        kws = dict(self.kwargs)
        kws.update(kwargs)
        return self.f(*ags, **kws)
        
class BindLastFunction(object):
    def __init__(self, f, *args, **kwargs):
        self.f = f
        self.args = list(args)
        self.kwargs = dict(kwargs)

    def __call__(self, *args, **kwargs):
        ags = list(args) + list(self.args)
        kws = dict(self.kwargs)
        kws.update(kwargs)
        return self.f(*ags, **kws)

def call_with_kwargs_filter(f, args, kwargs):
    #http://stackoverflow.com/questions/7628081/how-to-get-arguments-list-of-a-built-in-python-class-constructor
    #http://stackoverflow.com/questions/3999463/cant-get-argspec-for-python-callables
    g = f
    if inspect.isclass(f):
        g = f.__init__
    elif hasattr(f, '__call__'):
        g = f.__call__

    if isinstance(g, (types.FunctionType, types.MethodType)):
        arg, vararg, keyword, default = inspect.getargspec(g)
        DEBUG_('%s %s %s %s' % (arg, vararg, keyword, default))
        if keyword is None:
            keys = arg
            kwargs = sub_dict(kwargs, keys)

    return f(*args, **kwargs)

    
