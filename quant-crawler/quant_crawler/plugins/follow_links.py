from pyutils import *

from ..plugin import CrawlerPlugin
from ..response import Response
from ..exception import IgnoreRequest, IgnoreException
from ..utils import find_urls_in_html

class FollowLinksPlugin(CrawlerPlugin):
    def __init__(self, html_re=None, url_re=None, create_request=None):
        self.url_re = url_re
        self.html_re = html_re

        if create_request is None:
            create_request = self.create_request_default
        self.create_request = create_request


    def create_request_default(self, url, request=None, response=None):
        return Request(url=url)

    def find_urls(self, response):
        c = response.content
        return find_urls_in_html(c, html_re=self.html_re, url_re=self.url_re)

    def process_response(self, request, response, crawler):
        f = self.create_request
        if hasattr(crawler, 'create_request'):
            f = crawler.create_request

        base_url = request['url']
        for url in self.find_urls(response):
            url = urlparse.urljoin(base_url, url)
            yield f(url, request, response)


