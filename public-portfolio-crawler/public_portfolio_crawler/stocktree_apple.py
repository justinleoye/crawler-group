#coding: utf-8

from pyquery import PyQuery as pq
import re
import json

from pyutils import *
from quant_crawler import Crawler, Request, Response
from quant_serviced import serviced

from .utils import *
import datetime

class PublicStockTreeAppleCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']

        text = response.content
        table = pq(text)('#stock-holdings-table')
        assert table
        tbody = table('tbody').eq(0)
        assert tbody

        for tr in tbody.find('tr'):
            tr = pq(tr)
            order = tr('td').eq(0).html().replace('.)','')
            fund_name = tr('td').eq(1)('a').html()
            fund_managers = tr('td').eq(1)('p').html()
            shares = tr('td').eq(2).html().replace(',','')
            value = tr('td').eq(3).html().replace(',','').replace('$','')
            tr('td').eq(4)('img').remove()
            tr('td').eq(4)('span').remove()
            activity = tr('td').eq(4).html().replace('%','') if tr('td').eq(4).html() else ''
            portfolio_percent = tr('td').eq(5).html().replace('%','')

            d = {
                fields[0]: info['time'],
                fields[1]: info['symbol'],
                fields[2]: order,
                fields[3]: fund_name,
                fields[4]: fund_managers,
                fields[5]: num_normalize(shares),
                fields[6]: value_normalize(float_normalize(value)),
                fields[7]: percent_normalize(float_normalize(activity)),
                fields[8]: percent_normalize(float_normalize(portfolio_percent)),
            }
            d_json = {
                'type': 'hedge_fund',
                'time': d['time'],
                'hold_volume': d['shares'],
                'price': d['value']/d['shares'] if d['shares'] else None,
                'change_volume': None,
                'activity': d['activity'],
                'port': d['portfolio_percent']
            }
            try:
                f = open('stock_tree_apple.json','r')
                data_json = json.loads(f.read())
                f.close()
            except (IOError,ValueError),e:
                print e
                data_json = {}

            try:
                data_json[d['time']][d['fund_name']] = d_json
            except KeyError,e:
                print e
                data_json[d['time']] = {}
                data_json[d['time']][d['fund_name']] = d_json
            f = open('stock_tree_apple.json', 'w')
            f.write(json.dumps(data_json))
            f.close()

            yield d

    def tasks(self, job):
        params = {
            'cik': '320193',
            'time': '2013-12-31',
            'symbol': 'APPL',

        }

        for time in get_timestring_service('2013-09-30',False):
            params['time'] = time
            for symbol in ['AAPL']:
                params['symbol'] = symbol
                for i in range(12):
                    offset = i * 20
                    params['offset'] = offset
                    url = 'http://www.insidermonkey.com/get_fund_holdings.php?cik=%(cik)s&module=funds&ffp=%(time)s&fot=7&fso=1&offset=%(offset)s' % params

                    d = {
                        'url': url,
                        'target': '%s/%s/%s/%s' % (job['cache_path'],time,symbol, offset),
                        'task_id': '%s%s%s' % (time,symbol,offset),
                        'info': {
                            'fields': ['time','symbol','order','fund_name', 'fund_managers', 'shares', 'value', 'activity', 'portfolio_percent'],
                            'symbol': symbol,
                            'time': time

                        }
                    }
                    yield d
                
