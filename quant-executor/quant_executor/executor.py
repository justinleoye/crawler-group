

class Executor(object):
    def __call__(self, *args, **kwargs):
        return self.execute(*args, **kwargs)

    def execute(self, *args, **kwargs):
        return None

    def pause(self):
        pass

    def cont(self):
        pass
