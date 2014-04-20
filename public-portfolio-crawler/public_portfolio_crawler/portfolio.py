#coding:utf-8

import math
import json
from datetime import datetime
from pyquery import PyQuery as pq

from pyutils import *
from quant_crawler import Crawler, Request, Response

from quant_serviced import serviced

from .utils import *

def get_owned_funds(symbol):
    pass

class PublicCirculateStockHolderCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']

        text = response.content
        tree = pq(text)
        table = tree('#CirculateShareholderTable')
        assert table
        deadline = ''
        for tr in table.find('tr')[1::]:
            item = pq(tr)

            if item('strong'):
                if item('strong').html() == u'截止日期':
                    deadline = item('.tdr').html()
                continue
            if not item('div'):
                continue
            d = {
                'symbol': info['symbol'],
                fields[0]: date_normalize(deadline,'%Y-%m-%d'),
                fields[1]: num_normalize(item('div').eq(0).html()),
                fields[2]: item('div').eq(1).html(),
                fields[3]: num_normalize(item('div').eq(2).html()),
                fields[4]: percent_normalize(float_normalize(item('div').eq(3).html())),
                fields[5]: str_normalize(item('div').eq(4).html()),
            }
            yield d



    def tasks(self, job):
        print '++++++++++++++public++++++++++++++++++++++++'
        print repr(job)
        qd = job.get('quant_data')
        qd = serviced.get_service_client('quant_data.%s' % qd)
        symbols = qd.grep_symbols(job.get('symbols'))
        #qd.normalize_symbol()

        for symbol in symbols:
            params = {
                'symbol': public_symbol(symbol)
            }

            url = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CirculateStockHolder/stockid/%(symbol)s.phtml' % params

            d = {
                'url': url,
                'target': '%s/%s' % (job['cache_path'], symbol),
                'task_id': '%s' % (symbol),
                'info': {
                    'fields': ['deadline', 'order', 'holder_name', 'hold_volume', 'hold_percent', 'stock_property'],
                    'symbol': symbol
                }
            }
            yield d

class PublicStockHolderCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']
        symbol = info['symbol']

        text = response.content
        tree = pq(text)
        table = tree('#Table1')
        assert table
        deadline = ''
        publication_date = ''
        for tr in table.find('tr')[1::]:
            item = pq(tr)

            if item('strong'):
                if item('strong').html() == u'截止日期':
                    deadline = item('td').eq(1).html()
                if item('strong').html() == u'公告日期':
                    publication_date = item('td').eq(1).html()
                continue
            if not item('div'):
                continue
            d = {
                    fields[0]: symbol,
                    fields[1]: date_normalize(deadline, '%Y-%m-%d'),
                    fields[2]: date_normalize(publication_date, '%Y-%m-%d'),
                    fields[3]: num_normalize(item('div').eq(0).html()),
                    fields[4]: item('div').eq(1).html() if not item('div').eq(1)('a') else item('div').eq(1)('a').html(),
                    fields[5]: num_normalize(item('div').eq(2).html() if not item('div').eq(2)('a') else item('div').eq(2)('a').html()),
                    fields[6]: percent_normalize(float_normalize(item('div').eq(3).html() if not item('div').eq(3)('a') else item('div').eq(3)('a').html())),
                    fields[7]: str_normalize(item('div').eq(4).html()),
            }
            yield d


    def tasks(self, job):
        print '++++++++++++++++++++++++publicStockHolder++++++++++++++++++++++++++++++++++++'
        qd = job.get('quant_data')
        qd_client = serviced.get_service_client('quant_data.%s' % qd)
        symbols = qd_client.grep_symbols(job.get('symbols'))

        for symbol in symbols:
            params = {
                'symbol': public_symbol(symbol)
            }

            url = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_StockHolder/stockid/%(symbol)s.phtml' % params

            d = {
                'url': url,
                'target': '%s/%s' % (job['cache_path'], symbol),
                'task_id': '%s' % (symbol),
                'info': {
                    'fields': ['symbol', 'deadline', 'publication_date', 'order', 'holder_name', 'hold_volume', 'hold_percent', 'stock_property'],
                    'symbol': symbol
                }
            }
            yield d


class PublicFundStockHolderCrawler(Crawler):
    def process_response(self, request, response, crawler):
        info = request['info']

        if info['fund_stock_holder']:
            crawled = []
            text = response.content
            tree = pq(text)
            table = tree('#FundHoldSharesTable')
            assert table
            deadline = ''

            for tr in table.find('tr')[1::]:
                item = pq(tr)

                if item('strong'):
                    continue
                if not item('div'):
                    continue
                fund_id = item('div').eq(1).html()
                if not fund_id:
                    continue
                if fund_id in crawled:
                    continue

                params = {
                    'symbol': info['symbol'],
                    'fund_id': fund_id
                }
                url = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_FundOwnedList/stockid/%(symbol)s/fund_ownedid/%(fund_id)s.phtml' % params
                target = '%s/%s/%s' % (info['job_cache_path'], info['symbol'], fund_id),
                task_id = '%s%s' % (info['symbol'], fund_id),
                info =  {
                    'fields': ['symbol', 'fund_id', 'deadline', 'order', 'hold_name', 'hold_symbol', 'hold_volume', 'hold_value', 'hold_net_worth_percent'],
                    'symbol': info['symbol'],
                    'fund_id': fund_id,
                    'fund_stock_holder': False,
                    'job_cache_path': info['job_cache_path']
                }

                crawled.append(fund_id)
                print crawled
                yield Request(url=url, target=target, task_id=task_id, info=info, encoding=request.encoding)

    def filter(self, request, response):
        info = request['info']
        fields = info['fields']
        symbol = info['symbol']

        text = response.content
        tree = pq(text)
        if info['fund_stock_holder']:
            table = tree('#FundHoldSharesTable')
            assert table
            deadline = ''

            for tr in table.find('tr')[1::]:
                item = pq(tr)

                if item('strong'):
                    if item('strong').html() == u'截止日期':
                        deadline = item('td').eq(1).html()
                    continue
                if not item('div'):
                    continue
                d = {
                    fields[0]: symbol,
                    fields[1]: date_normalize(deadline, '%Y-%m-%d'),
                    fields[2]: item('div').eq(0)('a').html(),
                    fields[3]: item('div').eq(1).html(),
                    fields[4]: num_normalize(item('div').eq(2)('a').html()),
                    fields[5]: percent_normalize(float_normalize(item('div').eq(3).html())),
                    fields[6]: float_normalize(item('div').eq(4).html()),
                    fields[7]: percent_normalize(float_normalize(item('div').eq(5)('a').html())),
                }
                yield {'t1': d}
        else:
            table = tree('#Table1')
            assert table
            deadline = ''

            for tr in table.find('tr')[1::]:
                item = pq(tr)

                if item('strong'):
                    if item('strong').html() == u'截止日期':
                        deadline = item('td').eq(1).html()
                    continue
                if not item('div'):
                    continue
                if not item('div').eq(2).html():
                    continue
                d = {
                    fields[0]: symbol,
                    fields[1]: info['fund_id'],
                    fields[2]: date_normalize(deadline, '%Y-%m-%d'),
                    fields[3]: num_normalize(item('div').eq(0).html()),
                    fields[4]: item('div').eq(1).html(),
                    fields[5]: item('div').eq(2).html(),
                    fields[6]: num_normalize(item('div').eq(3).html()),
                    fields[7]: float_normalize(item('div').eq(4).html()),
                    fields[8]: percent_normalize(float_normalize(item('div').eq(5).html())),
                }
                yield {'t2': d}


    def tasks(self, job):
        print '++++++++++++++++publicFundStockHolder++++++++++++++++++'
        qd = job.get('quant_data')
        qd_client = serviced.get_service_client('quant_data.%s' % qd)
        symbols = qd_client.grep_symbols(job.get('symbols'))

        for symbol in symbols:
            params = {
                'symbol': public_symbol(symbol)
            }

            url = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_FundStockHolder/stockid/%(symbol)s.phtml' % params

            d = {
                'url': url,
                'target': '%s/%s' % (job['cache_path'], symbol),
                'task_id': '%s' % (symbol),
                'info': {
                    'fields': ['symbol', 'deadline', 'fund_name', 'fund_id', 'hold_volume', 'hold_percent', 'hold_value', 'hold_net_worth_percent'],
                    'symbol': symbol,
                    'fund_stock_holder': True,
                    'job_cache_path': job['cache_path']
                }
            }
            yield d


class PublicFundOwnedListCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']
        symbol = info['symbol']
        fund_id = info['fund_id']

        text = response.content
        tree = pq(text)
        table = tree('#Table1')
        assert table
        deadline = ''

        for tr in table.find('tr')[1::]:
            item = pq(tr)

            if item('strong'):
                if item('strong').html() == u'截止日期':
                    deadline = item('td').eq(1).html()
                continue
            if not item('div'):
                continue
            if not item('div').eq(2).html():
                continue
            d = {
                fields[0]: symbol,
                fields[1]: fund_id,
                fields[2]: date_normalize(deadline, '%Y-%m-%d'),
                fields[3]: num_normalize(item('div').eq(0).html()),
                fields[4]: item('div').eq(1).html(),
                fields[5]: item('div').eq(2).html(),
                fields[6]: num_normalize(item('div').eq(3).html()),
                fields[7]: float_normalize(item('div').eq(4).html()),
                fields[8]: percent_normalize(float_normalize(item('div').eq(5).html())),
            }
            yield d

    def tasks(self, job):
        qd = job.get('quant_data')
        qd_client = servied.get_service_client('quant_data.%s' % qd)
        symbols = qd_client.grep_symbols(job.get('symbols'))

        for symbol in symbols:
            for fund_id in get_owned_funds(symbol):
                params = {
                    'symbol': public_symbol(symbol),
                    'fund_id': fund_id
                }

                url = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_FundOwnedList/stockid/%(symbol)s/fund_ownedid/%(fund_id)s.phtml' % params

                d = {
                    'url': url,
                    'target': '%s/%s/%s' % (job['cache_path'], symbol, fund_id),
                    'task_id': '%s%s' % (symbol, fund_id),
                    'info': {
                        'fields': ['symbol', 'fund_id', 'deadline', 'order', 'hold_name', 'hold_symbol', 'hold_volume', 'hold_value', 'hold_net_worth_percent'],
                        'symbol': symbol,
                        'fund_id': fund_id
                        }
                }
                yield d
