from pyutils.log_utils import *

class MockObject(object):
    def __getattr__(self, attr):
        def f(*args, **kwargs):
            INFO("%s.%s: %s %s" % (self.__class__.__name__, attr, args, kwargs))
            
        return f

