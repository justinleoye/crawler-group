from pyutils import *
from pyutils import sleep_utils
from quant_executor.executor import Executor

class TestExecutor(Executor):
    def execute(self, job):
        name = job.get('name')
        count = job.get('count', 1)
        sleep = job.get('sleep', 1)
        echo =  job.get('echo')

        WARN("TestExecutor %s start [%s]" % (name, echo))
        INFO(echo)
        for i in range(count):
            INFO(echo)
            WARN("TestExecutor %s sleeping (%d/%d)..." % (name, i, count))
            sleep_utils.sleep(sleep)
        WARN("TestExecutor %s done" % name)

        
