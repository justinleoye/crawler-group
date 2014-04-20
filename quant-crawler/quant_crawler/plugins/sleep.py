import gevent

from pyutils import *
from pyutils import sleep_utils

from ..plugin import CrawlerPlugin
from ..exception import IgnoreRequest, IgnoreException

class SleepPlugin(CrawlerPlugin):
    def __init__(self, sleep=0, exception_sleep=0):
        self.sleep = sleep
        self.exception_sleep = exception_sleep

    def process_response(self, request, response, crawler):
        sleep_utils.sleep(self.sleep, "SleepPlugin.process_response")

    def process_exception(self, request, exception, crawler):
        sleep_utils.sleep(self.exception_sleep, "SleepPlugin.process_exception")


