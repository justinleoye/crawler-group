#conding: utf-8

from pyquery import PyQuery as pq
import re
import time

from pyutils import *
from quant_crawler import Crawler
from quant_serviced import serviced

from .utils import *

DATE_RE = re.compile(r'.*\d{4}-\d{2}-\d{2}.*')

class PublicRightsChangesHKCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields1 = info['fields1']
        fields2 = info['fields2']
        symbol = info['symbol']
        
        text = response.content
        html = pq(text)
        tbody_1 = html('#sub01_c2')('tbody')
        assert tbody_1
        tbody_2 = html('#sub01_c3')('tbody')
        assert tbody_1

        #filter main holder hold_change
        for tr in tbody_1.find('tr'):
            tr = pq(tr)
            if not DATE_RE.match(tr('td').eq(0).html()):
                #print '+++++++++++++'
                #print tr
                #print '+++++++++++++'
                #time.sleep(4)
                continue
            d = {
                fields1[0]: symbol,
                fields1[1]: datetime_utils.to_datetime(tr('td').eq(0).html()),
                fields1[2]: tr('td').eq(1).html(),
                fields1[3]: tr('td').eq(2).html(),
                fields1[4]: num_normalize(tr('td').eq(4).html()),# the eq(3) is dropped
                fields1[5]: percent_normalize(float_normalize(tr('td').eq(5).html())),
                fields1[6]: tr('td').eq(6).html(),
                fields1[7]: num_normalize(tr('td').eq(7).html()),
                fields1[8]: percent_normalize(float_normalize(tr('td').eq(8).html())),
                fields1[9]: tr('td').eq(9).html(),
                fields1[10]: tr('td').eq(10).html(),
            }
            yield {'t1': d}

        for tr in tbody_2.find('tr'):
            tr = pq(tr)
            if not DATE_RE.match(tr('td').eq(0).html()):
                #print '+++++++++++++'
                #print tr
                #print '+++++++++++++'
                #time.sleep(4)
                continue
            d = {
                fields2[0]: symbol,
                fields2[1]: datetime_utils.to_datetime(tr('td').eq(0).html()),
                fields2[2]: num_normalize(tr('td').eq(1).html()),
                fields2[3]: float_normalize(tr('td').eq(2).html()),
                fields2[4]: float_normalize(tr('td').eq(3).html()),
                fields2[5]: float_normalize(tr('td').eq(4).html()),
                fields2[6]: float_normalize(tr('td').eq(5).html()),
            }
            yield {'t2': d}

    def tasks(self, job):
        qd = job.get('quant_data')
        qd_client = serviced.get_service_client('quant_data.%s' % qd)
        symbols = qd_client.grep_symbols(job.get('symbols'))

        params = {
                'symbol': '00700',
        }
        #the list ['00005', '00857', '00700'] should change by symbols
        for symbol in ['00005', '00857', '00700']:
            params['symbol'] = symbol
            url = 'http://stock.finance.sina.com.cn/hkstock/rights/%(symbol)s.html' % params

            d = {
                'url': url,
                'target': '%s/%s' % (job['cache_path'], symbol),
                'task_id': '%s' % (symbol),
                'info': {
                    'fields1': ['symbol', 'time', 'holder_Chinese_name', 'holder_name', 'pre_hold_volume', 'pre_hold_percent', 'pre_hold_kind', 'hold_volume', 'hold_percent', 'hold_kind', 'stock_property'],
                    'fields2': ['symbol', 'time', 'volume', 'highest_price', 'lowest_price', 'value', 'average_price'],
                    'symbol': symbol
                }
            }
            yield d


