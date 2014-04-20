import math
import json
from datetime import datetime

from pyutils import *
from quant_crawler import Crawler

from quant_serviced import serviced

from .utils import *

"""
curl --compressed 'http://www.baring.cn:81/chartdata?callback=_jqjsp&symbol=IDDJSII&zb=MA*VOL*RSI&zq=min1&n=200&_1377320402349='

http://www.baring.cn:81/chartdata?callback=_jqjsp&symbol=CRXAU&zb=AMOUNT*VOL&zq=min1&n=200

curl --compressed 'http://www.baring.cn:81/chartdata?callback=_jqjsp&symbol=CRXAU&zb=AMOUNT*VOL&zq=min1&n=20000000'

n can be large: 137603, 188416, 
limited by resp size(?) or one year?


X([2,[2,[1377532800,86400],[140448,1124],[142340,1010],[139566,1756],[141500,533]],["AMOUNT",0,["",4,0,[53575780,-11739224]]],["VOL(5,10,20)",0,["",4,0,[37953,-8561]]]]);
"""

"""
http://www.baring.cn:3000/js/yt.data.js

"""                    

def filter_values_inc(a):
    n = len(a)
    b = list(a)
    for i in range(1,n):
        b[i] = b[i-1] + a[i]
    return b

def filter_values_digits(a, d):
    factor = math.pow(10, d)
    return [x*1.0/factor for x in a]

def filter_values_inc_digits(a, d):
    return filter_values_digits(filter_values_inc(a), d)

class YtcjKlineCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']
        m = []

        f = filter_values_inc_digits

        text = response.content.strip()[2:-2]
        data = json.loads(text)

        total = data[0]
        if total<=0:
            return

        ohlc = data[1]

        digits = ohlc[0]
        for i in range(1,len(ohlc)):
            if i==1:
                #time
                a = filter_values_inc(ohlc[i])
            else:
                #ohlc
                a = f(ohlc[i], digits)
            if len(a)!=total:
                raise Exception("array len error")
            m.append(a)

        for i in range(2, len(data)):
            a = data[i][2][3]
            digits = data[i][1]
            a = f(a, digits)
            if len(a)!=total:
                raise Exception("array len error")
            m.append(a)

        nf = len(fields)
        if nf!=len(m):
            print fields
            print len(m), len(m[0])
            raise Exception("fields len error: %d!=%d" % (nf, len(m)))

        for j in range(total):
            d = { 'symbol': info['symbol'] }
            for i in range(nf):
                f = fields[i]
                v = m[i][j]
                if f=='time':
                    v = datetime.fromtimestamp(v)
                d[f] = v
            yield d

    def tasks(self, job):
        print '++++++++++++++++++++++++++++++++++++++++++++++'
        print repr(job)
        BREAK_POINT()
        qd = job.get('quant_data') or 'futures'
        qd = serviced.get_service_client('quant_data.%s' % qd)
        symbols = qd.grep_symbols(job.get('symbols'))
        period = job.get('period', 'm1')
        count = job.get('count', 200)
        fields = job.get('fields', ['amount', 'volume'])

        period_map = {
            'm1': 'min1',
            'm5': 'min5',
            'm30': 'min30',
            'day': 'day',
            'week': 'week',
            'month': 'month'
        }

        indicator_map = {
            'amount': 'AMOUNT',
            'volume': 'VOL'
        }
        indicators = [indicator_map[f] for f in fields]

        for symbol in symbols:
            params = {
                'callback': 'X',
                'symbol': ytcj_symbol(symbol),
                'zq': period_map[period],
                'n': count,
                'zb': '*'.join(indicators),
            }

            #NOTE! url params order is important!
            url = 'http://www.baring.cn:81/chartdata?callback=%(callback)s&symbol=%(symbol)s&zb=%(zb)s&zq=%(zq)s&n=%(n)s' % params

            d = {
                'url': url,
                'target': '%s/%s/%s' % (job['cache_path'], period, symbol),
                'task_id': '%s:%s' % (period, symbol),
                'info': {
                    'fields': ['time', 'open', 'high', 'low', 'close'] + fields,
                    'symbol': symbol
                }
            }
            yield d
            
