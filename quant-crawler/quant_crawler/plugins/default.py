#import urllib2
#import httplib2
import gevent

from pyutils import *

from ..plugin import CrawlerPlugin
from ..exception import IgnoreRequest, IgnoreException
from ..response import Response
from ..fetch import fetch


class DefaultPlugin(CrawlerPlugin):
    def __init__(self, crawler_server=None):
        self.crawler_server = crawler_server

    def process_request(self, request, crawler):
        if self.crawler_server is not None:
            r = self.crawler_server.crawl(request)
            return Response.from_result(r)
        else:
            return fetch(request)

    def process_exception(self, request, exception, crawler):
        raise exception

