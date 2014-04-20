#coding: utf8

from gevent import monkey, sleep
monkey.patch_all()

from gevent.queue import Queue
from collections import defaultdict

from pyutils import *
from pyutils.datetime_utils import compare_datetime


from quant_func.symbol import *
from quant_crawler import Crawler

from .quotation import Quotation

class BaringQuote(object):
    def __init__(self, symbols=None, fields=None, socketio=None):
        if fields is None:
            fields = ["volume","amount","buys","sells","details","price","high","low","position","open","close","last_settle"]

        if socketio is None:
            host = 'www.baring.cn'
            port = 3000
            socketio = SocketIO(host, port)

        self.socketio = socketio
        self.quote = Quotation(symbols, fields)
        self.fields = fields
        self.symbols = symbols
        self.queue = Queue()

    def start(self):
        s = self.socketio
        s.on('ready', self.on_ready)
        s.on('quotation', self.on_quotation)
        s.on('disconnect', self.on_disconnect)
        s.start()

    def disconnect(self):
        s = self.socketio
        s.disconnect()

    def wait(self, secs=None):
        s = self.socketio
        s.wait(secs)

    def on_ready(self, *args):
        s = self.socketio

        s.emit('register fields', self.fields)
        s.emit('register symbols', map(ytcj_symbol, self.symbols))

    def on_quotation(self, *args):
        data = args[0]
        for r in self.quote.feed(data):
            if r is not None:
                DEBUG_(r)
                self.queue.put(r)

    def on_disconnect(self, *args):
        self.queue.put(None)

    def get(self):
        return self.queue.get()


class SocketioQuoteCrawler(Crawler):
    def tasks(self, job):
        yield {
            'socketio': {
                'host': 'www.baring.cn',
                'port': 3000
            },
            'info': {
                'job': job
            }
        }

    def filter(self, request, response):
        job = request['info']['job']
        exit_after = job.get('exit_after')
        fields = job.get('fields')
        symbols = job.get('symbols')

        bq = BaringQuote(symbols, fields, response.socketio)
        bq.start()
        while True:
            if exit_after:
                now = datetime.now()
                if compare_datetime(now, exit_after)>=0:
                    INFO("exit after %s, now %s" % (exit_after, now))
                    bq.disconnect()
                    break
            r = bq.get()
            if r is None:
                raise Exception("socketio disconnect")
            yield r

