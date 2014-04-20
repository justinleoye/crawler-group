#coding:utf-8

import math
import json
from datetime import datetime
from pyquery import PyQuery as pq
import copy

from pyutils import *
from quant_crawler import Crawler, Request, Response

from quant_serviced import serviced

from .utils import *

def get_table(text):
   # if not isinstance(text,unicode):
   #     text = text.decode('utf8')
   #     print type(text)
    tree = pq(text, parser='html')
    table = tree('#dataTable')
    assert table
    for thead in table('thead'):
        pq(thead).empty()

    return table

class ConsultNbjyCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']
        qd = info['qd']
        #qd_client = serviced.get_service_client('quant_data.%s' % qd)

        text = response.content
        table = get_table(text)
        
        for tr in table.find('tr'):
            item = pq(tr)

            if not item('td'):
                continue
            if not item('td').eq(9).html():
                continue

            change_kind = item('td').eq(3)('font').html() if item('td').eq(3)('font') else item('td').eq(3).html()
            change_hold = item('td').eq(4)('font').html() if item('td').eq(4)('font') else item('td').eq(4).html()
            deal_price = item('td').eq(5).html() if not item('td').eq(5)('font') else item('td').eq(5)('font').html()
            d = {
                #fields[0]: qd_client.normalize_symbol(item('td').eq(0)('a').html()),
                fields[0]: item('td').eq(0)('a').html(),
                fields[1]: str_normalize(item('td').eq(1)('a').html()),
                fields[2]: item('td').eq(2).html(),
                fields[3]: str_normalize(change_kind.strip()),
                fields[4]: num_normalize(change_hold.strip()),
                fields[5]: float_normalize(deal_price.strip()),
                fields[6]: value_normalize(float_normalize(item('td').eq(6).html()),'w'),
                fields[7]: num_normalize(item('td').eq(7).html()),
                fields[8]: str_normalize(item('td').eq(8).html()),
                fields[9]: datetime_utils.to_datetime(item('td').eq(9).html()),
                fields[10]: str_normalize(item('td').eq(10).html()),
                fields[11]: str_normalize(item('td').eq(11).html()),
                fields[12]: str_normalize(item('td').eq(12).html())
            }
            yield d


    def tasks(self, job):
        print '+++++++++++++ConsultNbjy++++++++++++++'
        qd = job.get('quant_data')

        # the mark for the last page
        page =  0
        for i in xrange(1,4542):
            page = i
            url = 'http://vip.stock.finance.sina.com.cn/q/go.php/vInvestConsult/kind/nbjy/index.phtml?num=40&bdate=1990-01-09&p=%s' % (page)

            d = {
                'url': url,
                'target': '%s/%s' % (job['cache_path'], page),
                'task_id': '%s' % (page),
                'info': {
                    'fields': ['symbol', 'name', 'changer_name', 'change_kind', 'change_hold', 'deal_price', 'change_value', 'after_change_hold', 'change_reason', 'time', 'hold_kind', 'relationship', 'position'],
                    'qd': qd,
                    'page': page
                }
            }
            yield d


class ConsultDzjyCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']
        qd = info['qd']
        qd_client = serviced.get_service_client('quant_data.%s' % qd)
        #qd.normalize_symbol(s)

        text = response.content
        table = get_table(text)
        
        for tr in table.find('tr'):
            item = pq(tr)

            if not item('td'):
                continue

            d = {
                fields[0]: datetime_utils.to_datetime(item('td').eq(0).html()),
                fields[1]: qd_client.normalize_symbol(item('td').eq(1)('a').html()),
                fields[2]: item('td').eq(2)('a').html(),
                fields[3]: float_normalize(item('td').eq(3).html()),
                fields[4]: volume_normalize(float_normalize(item('td').eq(4).html())),
                fields[5]: value_normalize(float_normalize(item('td').eq(5).html()),'w'),
                fields[6]: str_normalize(item('td').eq(6).html()),
                fields[7]: str_normalize(item('td').eq(7).html()),
                fields[8]: str_normalize(item('td').eq(8).html())
            }
            yield d


    def tasks(self, job):
        print '+++++++++++++ConsultNbjy++++++++++++++'
        qd = job.get('quant_data')

        # the mark for the last page
        page =  0
        for i in xrange(1,745):
            page = i
            url = 'http://vip.stock.finance.sina.com.cn/q/go.php/vInvestConsult/kind/dzjy/index.phtml?num=40&bdate=1990-01-09&p=%s' % (page)

            d = {
                'url': url,
                'target': '%s/%s' % (job['cache_path'], page),
                'task_id': '%s' % (page),
                'info': {
                    'fields': ['time', 'symbol', 'name', 'deal_price', 'deal_volume', 'deal_value', 'buyer', 'seller', 'hold_kind'],
                    'qd': qd,
                    'page': page
                }
            }
            yield d


class ConsultXsjjCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']
        qd = info['qd']
        qd_client = serviced.get_service_client('quant_data.%s' % qd)
        #qd.normalize_symbol(s)

        text = response.content
        table = get_table(text)
        
        for tr in table.find('tr'):
            item = pq(tr)

            if not item('td'):
                continue

            d = {
                fields[0]: qd_client.normalize_symbol(item('td').eq(0)('a').html()),
                fields[1]: item('td').eq(1)('a').html(),
                fields[2]: datetime_utils.to_datetime(item('td').eq(2).html()),
                fields[3]: num_normalize(item('td').eq(3).html()),
                fields[4]: datetime_utils.to_datetime(item('td').eq(4).html()),
                fields[5]: volume_normalize(float_normalize(item('td').eq(5).html())),
                fields[6]: value_normalize(float_normalize(item('td').eq(6).html()),'y'),
                fields[7]: datetime_utils.to_datetime(item('td').eq(7).html()),
                fields[8]: datetime_utils.to_datetime(item('td').eq(8).html())
            }
            yield d


    def tasks(self, job):
        print '+++++++++++++ConsultNbjy++++++++++++++'
        qd = job.get('quant_data')

        # the mark for the last page
        page =  0
        for i in xrange(1,212):
            page = i
            url = 'http://vip.stock.finance.sina.com.cn/q/go.php/vInvestConsult/kind/xsjj/index.phtml?num=40&bdate=1990-01-09&p=%s' % (page)

            d = {
                'url': url,
                'target': '%s/%s' % (job['cache_path'], page),
                'task_id': '%s' % (page),
                'info': {
                    'fields': ['symbol', 'name', 'time', 'listed_batches', 'up_to_listed_date', 'volume', 'value', 'start_date', 'end_date'],
                    'qd': qd,
                    'page': page
                }
            }
            yield d

class ConsultLsfhCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']
        qd = info['qd']
        qd_client = serviced.get_service_client('quant_data.%s' % qd)
        #qd.normalize_symbol(s)

        text = response.content
        table = get_table(text)
        
        for tr in table.find('tr'):
            item = pq(tr)

            if not item('td'):
                continue

            d = {
                fields[0]: qd_client.normalize_symbol(item('td').eq(0)('a').html()),
                fields[1]: item('td').eq(1)('a').html(),
                fields[2]: datetime_utils.to_datetime(item('td').eq(2).html()),
                fields[3]: percent_normalize(float_normalize(item('td').eq(3).html())),
                fields[4]: percent_normalize(float_normalize(item('td').eq(4).html())),
                fields[5]: num_normalize(item('td').eq(5).html()),
                fields[6]: value_normalize(float_normalize(item('td').eq(6).html()),'y'),
                fields[7]: num_normalize(item('td').eq(7).html()),
                fields[8]: item('td').eq(8)('a').attr('href')
            }
            yield d


    def tasks(self, job):
        print '+++++++++++++ConsultLsfh++++++++++++++'
        qd = job.get('quant_data')

        # the mark for the last page
        page =  0
        for i in xrange(1,63):
            page = i
            url = 'http://vip.stock.finance.sina.com.cn/q/go.php/vInvestConsult/kind/lsfh/index.phtml?num=40&bdate=1990-01-09&p=%s' % (page)

            d = {
                'url': url,
                'target': '%s/%s' % (job['cache_path'], page),
                'task_id': '%s' % (page),
                'info': {
                    'fields': ['symbol', 'name', 'time', 'acc_dividend', 'average_dividend', 'fh_times', 'total_financing', 'financing_times', 'details'],
                    'qd': qd,
                    'page': page
                }
            }
            yield d
