import gevent
import os
from datetime import datetime

from pyutils import *
from pyutils import sleep_utils
from quant_qdb.qdb_dict import QdbDict
import quant_dbi.qdb

from ..plugin import CrawlerPlugin
from ..response import Response
from ..exception import IgnoreRequest, IgnoreException

class QdbCachePlugin(CrawlerPlugin):
    def __init__(self, table=None, zip=False, auto_skip=True, sleep_if_no_cache=None):
        if is_str(table):
            table = quant_dbi.qdb.stream_to_table(table)

        if zip:
            zip_fields = ['content']
        else:
            zip_fields = None
        self.cache = QdbDict(table, key_field='url', zip_fields=zip_fields)

        self.auto_skip = auto_skip
        self.sleep_if_no_cache = sleep_if_no_cache
        self._first = True

    def process_request(self, request, crawler):
        url = request.get('url')
        obj = self.cache.get(url)

        if self.auto_skip and obj is not None:
            INFO("skip as target already exists")
            content = obj['content']
            headers = obj.get('headers', {})
            r = Response(headers=headers)
            r.set_content(content)
            r.set_encoding(request.encoding)
            r.cached = True
            return r

    def process_response(self, request, response, crawler):
        if not response.cached:
            obj = {
                'content': response.content,
                'headers': dict(response.headers),
                'time': datetime.now(),
            }
            self.cache[request.url] = obj
            
            s = self.sleep_if_no_cache
            #don't sleep for first response
            if s is not None and not self._first:
                sleep_utils.sleep(s, 'QdbCachePlugin: no_cache')
            self._first = False


