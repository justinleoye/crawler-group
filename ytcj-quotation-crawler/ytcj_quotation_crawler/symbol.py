import math
import json
from datetime import datetime

import js_object_parser
import execjs

from pyutils import *
from quant_crawler import Crawler

from .utils import *


class YtcjSymbolCrawler(Crawler):
    def filter(self, request, response):
        #TODO
        #cause exception 
        #Exception AttributeError: AttributeError("'_DummyThread' object has no attribute '_Thread__block'",) in <module 'threading' from '/usr/lib64/python2.7/threading.pyc'> ignored

        js = response.text
        c = execjs.compile(js)
        for s in c.eval('yt.symbols'):
            d = {
                'symbol': normalize_ytcj_symbol(s[0]),
                'name': s[1],
                'abbr': s[2],
                'exchange': s[0][:2],
            }
            yield d

    def tasks(self, job):
        d = {
            'url': 'http://www.baring.cn:3000/js/yt.js'
        }
        yield d

