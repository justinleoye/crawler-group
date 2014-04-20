import urlparse
from pyquery import PyQuery
import re

from pyutils import *
from pyutils.create_obj import create_obj_with_import
from pyutils.mock_utils import MockObject

def find_urls_in_html(html, html_re=None, url_re=None):

    if is_str(html_re):
        html_re = re.compile(html_re)

    if is_str(url_re):
        html_re = re.compile(url_re)

    if self.html_re:
        for url in self.html_re.findall(html):
            yield url

    if self.url_re:
        h = PyQuery(html)
        for a in h('a'):
            url = a.attr.href
            if self.url_re.match(url):
                yield url

def test_crawler_job(job):
    master = MockObject()
    kwargs = {
        'event_manager': master,
    }
    crawler = create_obj_with_import(job, 'crawler', kwargs=kwargs)
    stream = crawler.feed(job)
    for x in stream:
        DEBUG(x)


