
class JobPlugin(object):
    def __init__(self, worker=None, **kwargs):
        self.worker = worker
        self.init(**kwargs)

    def accept(self, job):
        #is plugin applicable for this job?
        return True

    def init(self, **kwargs):
        pass

    def on_done(self, job):
        pass

    def on_fail(self, job):
        pass

    def on_start(self, job):
        pass

    def on_stop(self, job):
        pass

    def on_pause(self, job):
        pass

    def on_continue(self, job):
        pass

    def on_schedule(self, job):
        pass

