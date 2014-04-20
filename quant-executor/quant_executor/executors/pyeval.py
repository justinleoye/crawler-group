from pyutils import *
from pyutils.create_obj import load_variable
from quant_executor.executor import Executor

class PyEvalExecutor(Executor):
    def execute(self, job):
        func = job.get('func')
        f = load_variable(func)
        if f is None:
            raise Exception("func not found: %s" % func)
        args = job.get('args', [])
        kwargs = job.get('kwargs', {})
        r = f(*args, **kwargs)
        return r

