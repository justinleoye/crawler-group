import gevent

from pyutils import *
from pyutils import sleep_utils

from ..plugin import CrawlerPlugin
from ..exception import IgnoreRequest, IgnoreException

class RetryPlugin(CrawlerPlugin):
    def __init__(self, max_retry=None, retry_sleep=None):
        if max_retry is None:
            max_retry = 0

        if retry_sleep is None:
            retry_sleep = 5

        self.max_retry = max_retry
        self.retry_sleep = retry_sleep

    def process_exception(self, request, exception, crawler):
        if not '__retry__' in request:
            request['__retry__'] = 0
        retry = request['__retry__']
        if retry < self.max_retry:
            ERROR('retry num: %s<=%s:\nexception:\n%s\nrequest:\n%s' %\
                (retry, self.max_retry, exception, request))
            request['__retry__'] += 1
            sleep_utils.sleep(self.retry_sleep, 'RetryPlugin.retry')
            return request
        else:
            ERROR('max retry limit reached %s>=%s:\nexception:\n%s\nrequest:\n%s' %\
                (retry, self.max_retry, exception, request))

        

