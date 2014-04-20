from pyutils import *

from ..plugin import CrawlerPlugin
from ..exception import IgnoreRequest, IgnoreException

class FailurePlugin(CrawlerPlugin):
    def __init__(self, ignore=False):
        self.ignore = ignore

    def process_exception(self, request, exception, crawler):
        if self.ignore:
            raise IgnoreException()



