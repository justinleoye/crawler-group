#coding: utf8

from datetime import datetime
from collections import defaultdict

from pyutils import *
from updater import Updater

"""
volume: 成交量
amount: 成交额
position: 持仓量
"""

class QuotationToTickUpdater(Updater):
    def __init__(self):
        self.last_vols = {}

    def feed(self, rec):
        s = rec['symbol']
        last_vol = self.last_vols.get(s, 0)
        ticks = Quotation.ticks(rec, last_vol)
        self.last_vols[s] = rec.get('volume')
        yield list(ticks)

        #ticks = sorted(ticks, key=lambda x: (x['time'], x['volume']))
        #for t in ticks:
        #    yield t

class Quotation(object):
    def __init__(self, symbols=None, fields=None, debug=False, prefix=None):
        self.fields = fields
        self.symbols = symbols

        #'data:'
        self.prefix = prefix

        self.debug = debug
        self.quotes = defaultdict(dict)
        self.last_volumes = defaultdict(int)
        self.first_pass = True

    def feed_line(self, line):
        if not line:
            return
        if self.debug:
            DEBUG(line)
        if self.prefix:
            if not line.startswith(self.prefix):
                return
            line = line[len(self.prefix):]
        try:
            r = js_object_parser.loads(line)
            for x in self.feed(r):
                yield x
        except Exception, e:
            ERROR("[RealtimeQuote] parse error: %s, line %s" % (e, line))
            if self.debug:
                raise

    def get_quote(self, q, a, symbol):
        changed = False
        fields = self.fields
        m = min(len(a), len(fields))
        div = math.pow(10, q['digits'])
        for i in range(m):
            v = a[i]
            if v is None:
                continue
            f = fields[i]
            if not f in q:
                if f in ['volume', 'amount', 'buys', 'sells', 'details']:
                    q[f] = v
                else:
                    q[f] = v / div
            else:
                if f in ['buys', 'sells', 'details']:
                    n = len(v)
                    if f=='details':
                        DEBUG_('%s' % v[::4])
                        for i in range(n):
                            if i%4==1:
                                v[i] /= div
                    else:
                        for i in range(n):
                            if i%2==0:
                                v[i] /= div

                    for i in range(n):
                        q[f][i] += v[i]

                else:
                    if f not in ['volume', 'amount']:
                        v /= div
                    q[f] += v
            changed = True
        if changed:
            if not 'time' in q:
                q['time'] = datetime.now()
            return q
        else:
            return None

    @classmethod
    def ticks(cls, q, last_vol):
        v = q.get('details')
        if v is None:
            d = {
                'symbol': q['symbol'],
                'name': q['name'],
                'price': q['price'],
                'volume': q['volume'],
                'amount': q['amount']
            }
            yield d
        else:
            n = len(v)
            for i in range(0,n-4,4):
                t, price, vol, pos = v[i:i+4]
                if vol <= last_vol or v[i+6]<=0:
                    continue
                vol = v[i+2] - v[i+6]
                if vol<0:
                    break
                else:
                    pos -= v[i+1]
                d = {
                    'symbol': q['symbol'],
                    'name': q['name'],
                    'time': datetime.fromtimestamp(t),
                    'price': price,
                    'volume': vol,
                    'amount': vol*price,
                    'position': pos
                }
                yield d

    def feed(self, r):
        #NOTE: don't modify result returned
        if not r:
            return
        for a in r:
            symbol = self.symbols[a[0]]
            q = self.quotes[symbol]

            if self.first_pass:
                #symbol, name, digit, init_data
                #digit 调整数字, 如价格1000显示为1/100元(digit=2)
                #[["IDNICI","日经指数",2,1451483,...], ... ["HKHSIO","恒生指数",2,2270707...],]
                q.update({
                    'symbol': symbol,
                    'name': a[1],
                    'digits': a[2]
                })
                d = self.get_quote(q, a[3:], symbol)
            else:
                #data:[[2,-2,,,,,-2],]
                if not a:
                    continue
                d = self.get_quote(q, a[1:], symbol)

            if d is not None:
                yield d

        self.first_pass = False

#[id, "volume","amount","buys","sells","details","price","high","low","position","open","close","last_settle"]
"""
[[2026, 1623, 1468816, [-1, -648, 903, 847, 902, 280, 901, 295, 900, 1133], [0, -1171, 906, 871, 907, 157, 908, 614, 909, 413], [228, 0, 1623, 0, 19, 0, 42, 0, 29, 0, 381, 0, 22, 0, 405, 0, 21, 2, 929, 0, 24, -1, 394, 0, 16, 0, 292, 0, 15, -1, 154, 0, 31, 0, 863, 0, 20, 1, 171, 0, 15, 0, 120, 0], 0, 0, 0, 0, 0, 0, 0]]
"""

#http://www.baring.cn:3000/js/yt.js

