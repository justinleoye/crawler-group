import gevent
import os
from datetime import datetime

from pyutils import *

from ..plugin import CrawlerPlugin
from ..response import Response
from ..exception import IgnoreRequest, IgnoreException


class SkipDonePlugin(CrawlerPlugin):
    def __init__(self):
        pass

    def get_skip_done(self, request, crawler):
        s = request.get('skip_done') or crawler.skip_done or {}
        if not 'event' in s:
            t = request.get('task_id')
            if t is None:
                return None
            s['event'] = t
        return s

    def process_request(self, request, crawler):
        s = self.get_skip_done(request, crawler)
        if s is None:
            return

        em = crawler.event_manager
        url = request.url
        e = 'crawler:done:' + s.get('event')
        if not s.get('always_run') and em.check_event(e, s.get('within')):
            INFO("[CrawlerSkipDonePlugin] skip done request: %s event: %s" % (url, e))
            request['__skipped_at__'] = datetime.now()
            raise IgnoreRequest()

    def process_done(self, request, crawler):
        s = self.get_skip_done(request, crawler)
        if s is None:
            return

        em = crawler.event_manager
        #don't fire done event again if skipped
        if request.get('__skipped_at__'):
            return
        e = 'crawler:done:' + s.get('event')
        em.fire_event(e)


