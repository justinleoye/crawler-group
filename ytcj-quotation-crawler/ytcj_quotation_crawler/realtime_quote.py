# coding:utf8

import json
import gevent
import js_object_parser
from datetime import datetime

from pyutils import *
from quant_func.symbol import *
from quant_crawler import *
from updater import *

from .utils import ytcj_symbol

"""
agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31'
referer='http://3.baring.cn/quo/bin/quotation.dll/page/ytcj.com.CURR.htm'
curl -A "$agent" --referer $referer 'http://1.baring.cn/quo/bin/quotation.dll?fields=Price,LastSettle,Open,Close,High,Low,Volume,Amount&symbols=SH1A0001'

curl -A "$agent" --referer $referer 'http://1.baring.cn/quo/bin/quotation.dll?fields=Price,LastSettle,Open,Close,High,Low,Volume,Amount&symbols=SH1A0001,SZ399001,HKHSIO,NSINDIW,IDNQCI,IDNICI,USDINIW,IDDAX,CRXAU,CRXAG,CRXPD,CRXAP,SQAUS0,SQALS2,SQNRF0,SQFUS0,ZQSRZ0,DQPOD0,SQCOS0,CXGLN0,CXSLN0,NYHON0,NYCON0,USDINIW,USAUDUSD,USEURUSD,USGBPUSD,USNZDUSD,USUSDCAD,USUSDCHF,USUSDCNY,USUSDHKD,USUSDJPY,USUSDMOP,USUSDSGD,USUSDMYR,USUSDTWD,'
"""

"""
data:[["IDNICI","日经指数",2,1451483,1563548,1573998,1563548,1594260,1451483],["IDDAX","法 DAX指",2,0,853089,0,853089,0,0],["USDINIW","美元指数",2,8417,8429,8429,8429,8449,8417],["NSINDIW","道琼指数",2,1530587,1538758,1538712,1538712,1554240,1526409],["IDNQCI","纳斯达克",2,0,346330,0,346330,0,0],["SH1A0001","上证指数",2,227567,230240,229381,230240,230495,227410],["SZ399001","深证成指",2,926567,940506,936273,940506,944540,924246],["HKHSIO","恒生指数",2,2270707,2326108,2306671,2326108,2312343,2260569],]

data:[[7,1],]
...
data:[[2],[7,163],]
...
data:[[2,-2,,,,,-2],]
...
#法 DAX指 初始收到的值为0,所以增量比较大
data:[[1,835216,,835216,,853089,835216],[7,249],]
data:[[7,-161],]
"""

class RealtimeQuoteCrawler(Crawler):
    def tasks(self, job):
        symbols = job.get('symbols')
        fields = job.get('fields')

        if symbols is None or symbols=='index':
            index = 'SH1A0001 SZ399001 HKHSIO NSINDIW IDNQCI IDNICI USDINIW IDDAX'
            gold = 'CRXAU CRXAG CRXPD CRXAP'
            future = 'SQAUS0 SQALS2 SQNRF0 SQFUS0 ZQSRZ0 DQPOD0 SQCOS0 CXGLN0 CXSLN0 NYHON0 NYCON0'
            forex = 'USDINIW USAUDUSD USEURUSD USGBPUSD USNZDUSD USUSDCAD USUSDCHF USUSDCNY USUSDHKD USUSDJPY USUSDMOP USUSDSGD USUSDMYR USUSDTWD'
            symbols = ('%s %s %s %s' % (index, gold, future, forex)).split()

        elif is_str(symbols):
            symbols = list(GREP_SYMBOLS(symbols))

        self.symbols = map(ytcj_symbol, symbols)

        if fields is None:
            fields = 'Price LastSettle Open Close High Low Volume Amount'.split()

        self.fields = fields
        self.first_pass = True
        self.debug = job.get('debug')
        
        #NOTE: comma after last field and symbol is NEEDED
        data = {
            'fields': ','.join(self.fields)+',',
            'symbols': ','.join(self.symbols)+','
        }
        url = 'http://1.baring.cn/quo/bin/quotation.dll?fields=%(fields)s&symbols=%(symbols)s' % data

        while True:
            yield {
                'streaming': True,
                'chunk_size': 8,
                'url': url,
                'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31',
                'referer': 'http://3.baring.cn/quo/bin/quotation.dll/page/ytcj.com.CURR.htm'
            }
            gevent.sleep(30)

    def filter(self, request, response):
        for line in response.lines:
            for r in self.filter_line(line):
                yield r

    def mapped_fields(self, fields):
        fields_mapper = {
            'Price': 'price',
            'LastSettle': 'last_close',
            'Open': 'open',
            'Close': 'close',
            'High': 'high',
            'Low': 'low',
            'Volume': 'volume',
            'Amount': 'amount'
        }
        return [fields_mapper[f] for f in fields]

    def get_quote(self, q, a, div=True):
        changed = False
        fields = self.mapped_fields(self.fields)
        m = min(len(a), len(fields))
        for i in range(m):
            if a[i] is not None:
                f = fields[i]
                q[f] = q.get(f,0) + a[i]
                changed = True
        if changed:
            d = dict(q)
            if div:
                for f in 'price last_close open close high low'.split():
                    if d.get(f) is not None:
                        d[f] = d[f]/100.0
            d['time'] = datetime.now()
            return d

    def filter_line(self, line):
        if not line:
            return
        if self.debug:
            DEBUG(line)
        if not line.startswith('data:'):
            return
        try:
            r = js_object_parser.loads(line[5:])
            try:
                if self.first_pass:
                    self.first_pass = False

                    #symbol, name, digit, init_data
                    #digit 用于显示, 如100股显示为1手(digit=2)
                    #[["IDNICI","日经指数",2,1451483,...], ... ["HKHSIO","恒生指数",2,2270707...],]
                    self.n = len(r)
                    self.quotes = []
                    for a in r:
                        q = {
                            'symbol': normalize_ytcj_symbol(a[0]),
                            'name': a[1],
                            #'digit': a[2], #no use
                        }
                        d = self.get_quote(q, a[3:], div=True)
                        self.quotes.append(q)
                        if d is not None:
                            DEBUG_(d)
                            yield d
                else:
                    #data:[[2,-2,,,,,-2],]
                    for a in r:
                        if not a:
                            continue
                        q = self.quotes[a[0]]
                        d = self.get_quote(q, a[1:], div=True)
                        if d is not None:
                            DEBUG_(d)
                            yield d

            except Exception, e:
                ERROR("[RealtimeQuote] data error: %s, line %s" % (e, line))
                if self.debug:
                    raise
        except Exception, e:
            ERROR("[RealtimeQuote] parse error: %s, line %s" % (e, line))
            if self.debug:
                raise

