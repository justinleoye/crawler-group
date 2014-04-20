from pyutils.sleep_utils import sleep

class Pausable(object):
    def __init__(self):
        self.paused = False

    def pause(self):
        self.paused = True

    def cont(self):
        self.paused = False

    def wait_if_paused(self, wait=1):
        while self.paused:
            sleep(wait, self.__class__.__name__)

