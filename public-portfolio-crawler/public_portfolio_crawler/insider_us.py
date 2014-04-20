#coding: utf-8

from pyquery import PyQuery as pq

from pyutils import *
from quant_crawler import Crawler
from quant_serviced import serviced

from .utils import *

def fake_us_symbol_service(qd):
    for i in ['AAPL']:
        yield i

def value_normalize_for_MSN_Money(s):
    #print s
    if s == 'NA':
        return None
    if s.endswith('Mil'):
        #print 'Mil'
        s = s.replace('Mil','').replace(',','').strip()
        s = float_normalize(s)
        if s != None:
            return s * 1000000
        return None
    if s.endswith('Bil'):
        #print 'Bil'
        s = s.replace('Bil','').replace(',','').strip()
        s = float_normalize(s)
        if s != None:
            return s * 1000000000
        return None
    s = s.replace(',','').strip()
    return float_normalize(s)

def volume_normalize_for_MSN_Money(s):
    if s:
        s = s.replace(',', '').strip()
        s = num_normalize(s)
        return s
    return None

class PublicInsiderTransactionUSCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']

        text = response.content
        table = pq(text)('table')('.mnytbl')
        assert table
        tbody = table('tbody')
        assert tbody
        for tr in tbody.find('tr'):
            tr = pq(tr)

            time = tr('td[headers="datehead"]')('span').html().replace('\r','').replace('\n','').strip()
            name = tr('td[headers="namehead"]').html().replace('\r','').replace('\n','').strip()
            transaction = tr('td[headers="transhead"]')('span').html().replace('\r','').replace('\n','').strip()
            volume = tr('td[headers="shareshead"]')('span').html().replace('\r','').replace('\n','').strip()
            price = tr('td[headers="pricehead"]')('span').html().replace('\r','').replace('\n','').strip()
            value = tr('td[headers="valuehead"]')('span').html().replace('\r','').replace('\n','').strip()
            d = {
                fields[0]: info['symbol'],
                fields[1]: datetime_utils.to_datetime(time),
                fields[2]: name,
                fields[3]: transaction,
                fields[4]: volume_normalize_for_MSN_Money(volume),
                fields[5]: float_normalize(price),
                fields[6]: value_normalize_for_MSN_Money(value),
            }
            #if info['symbol'] == 'AAPL':
                #d_json = {
                #    'time': d['time'],
                #    'symbol': d['symbol'],
                #    'name': d['name'],
                #    'transaction': d['transaction'],
                #    'volume': d['volume'],
                #    'value': d['value']

                #}
                #try:
                #    f = open()
            yield d

    def tasks(self, job):
        qd = job.get('quant_data')

        params = {
            'view': 'All',
            'symbol': 'A'
        }

        for symbol in fake_us_symbol_service(qd):
            params['symbol'] = symbol
            url = 'http://investing.money.msn.com/investments/insider-transactions?view=%(view)s&symbol=%(symbol)s' % params

            d = {
                'url': url,
                'target': '%s/%s' % (job['cache_path'], symbol),
                'task_id': '%s' % (symbol),
                'info':{
                    'fields': ['symbol', 'time', 'trader_name', 'transaction', 'volume', 'price', 'value'],
                    'symbol': symbol
                }
            }
            yield d

class PublicTopInstitutionalHoldersUSCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']

        text = response.content
        table = pq(text)('table')('.mnytbl').eq(2)
        assert table
        tbody = table('tbody')
        assert tbody
        for tr in tbody.find('tr'):
            tr = pq(tr)

            institution_name = tr('td').eq(0)('span').html().replace('\r','').replace('\n','').strip()
            held_volume = tr('td').eq(1)('span').html().replace('\r','').replace('\n','').strip()
            change_volume = (tr('td').eq(2)('span') if not tr('td').eq(2)('span')('span[class="down"]') else tr('td').eq(2)('span')('span[class="down"]')).html().replace('\r','').replace('\n','').strip()
            change_percent = (tr('td').eq(3)('span') if not tr('td').eq(3)('span')('span[class="down"]') else tr('td').eq(3)('span')('span[class="down"]')).html().replace('\r','').replace('\n','').strip()
            change_value = (tr('td').eq(4)('span') if not tr('td').eq(4)('span')('span[class="down"]') else tr('td').eq(4)('span')('span[class="down"]')).html().replace('\r','').replace('\n','').strip()
            outstanding_percent = (tr('td').eq(5)('span') if not tr('td').eq(5)('span')('span[class="down"]') else tr('td').eq(5)('span')('span[class="down"]')).html().replace('\r','').replace('\n','').strip()
            portfolio_percent = (tr('td').eq(6)('span') if not tr('td').eq(6)('span')('span[class="down"]') else tr('td').eq(6)('span')('span[class="down"]')).html().replace('\r','').replace('\n','').strip()
            time = tr('td').eq(7)('span').html().replace('\r','').replace('\n','').strip()

            #print [institution_name, held_volume, change_volume, change_percent]
            d = {
                fields[0]: info['symbol'],
                fields[1]: institution_name,
                fields[2]: volume_normalize_for_MSN_Money(held_volume),
                fields[3]: volume_normalize_for_MSN_Money(change_volume),
                fields[4]: percent_normalize(float_normalize(change_percent)),
                fields[5]: value_normalize_for_MSN_Money(change_value),
                fields[6]: percent_normalize(float_normalize(outstanding_percent)),
                fields[7]: percent_normalize(float_normalize(portfolio_percent)),
                fields[8]: datetime_utils.to_datetime(time),
            }
            yield d

    def tasks(self, job):
        qd = job.get('quant_data')

        params = {
            'symbol': 'A',
        }

        for symbol in fake_us_symbol_service(qd):
            params['symbol'] = symbol
            url = 'http://investing.money.msn.com/investments/institutional-ownership?symbol=%(symbol)s' % params

            d = {
                'url': url,
                'target': '%s/%s' % (job['cache_path'], symbol),
                'task_id': '%s' % (symbol),
                'info':{
                    'fields': ['symbol', 'institution_name', 'held_volume', 'change_volume', 'change_percent', 'change_value', 'outstanding_percent', 'portfolio_percent', 'time'],
                    'symbol': symbol
                }
            }
            yield d

class PublicTopMutualFundHoldersUSCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']

        text = response.content
        table = pq(text)('table')('.mnytbl').eq(2)
        assert table
        tbody = table('tbody')
        assert tbody
        for tr in tbody.find('tr'):
            tr = pq(tr)

            mutual_fund_name = tr('td').eq(0)('span').html().replace('\r','').replace('\n','').strip()
            held_volume = tr('td').eq(1)('span').html().replace('\r','').replace('\n','').strip()
            change_volume = (tr('td').eq(2)('span') if not tr('td').eq(2)('span')('span[class="down"]') else tr('td').eq(2)('span')('span[class="down"]')).html().replace('\r','').replace('\n','').strip()
            change_percent = (tr('td').eq(3)('span') if not tr('td').eq(3)('span')('span[class="down"]') else tr('td').eq(3)('span')('span[class="down"]')).html().replace('\r','').replace('\n','').strip()
            change_value = (tr('td').eq(4)('span') if not tr('td').eq(4)('span')('span[class="down"]') else tr('td').eq(4)('span')('span[class="down"]')).html().replace('\r','').replace('\n','').strip()
            outstanding_percent = (tr('td').eq(5)('span') if not tr('td').eq(5)('span')('span[class="down"]') else tr('td').eq(5)('span')('span[class="down"]')).html().replace('\r','').replace('\n','').strip()
            portfolio_percent = (tr('td').eq(6)('span') if not tr('td').eq(6)('span')('span[class="down"]') else tr('td').eq(6)('span')('span[class="down"]')).html().replace('\r','').replace('\n','').strip()
            time = tr('td').eq(7)('span').html().replace('\r','').replace('\n','').strip()

            #print [mutual_fund_name, held_volume, change_volume, change_percent]
            d = {
                fields[0]: info['symbol'],
                fields[1]: mutual_fund_name,
                fields[2]: volume_normalize_for_MSN_Money(held_volume),
                fields[3]: volume_normalize_for_MSN_Money(change_volume),
                fields[4]: percent_normalize(float_normalize(change_percent)),
                fields[5]: value_normalize_for_MSN_Money(change_value),
                fields[6]: percent_normalize(float_normalize(outstanding_percent)),
                fields[7]: percent_normalize(float_normalize(portfolio_percent)),
                fields[8]: datetime_utils.to_datetime(time),
            }
            yield d

    def tasks(self, job):
        qd = job.get('quant_data')

        params = {
            'symbol': 'A',
        }

        for symbol in fake_us_symbol_service(qd):
            params['symbol'] = symbol
            url = 'http://investing.money.msn.com/investments/mutual-fund-ownership?symbol=%(symbol)s' % params

            d = {
                'url': url,
                'target': '%s/%s' % (job['cache_path'], symbol),
                'task_id': '%s' % (symbol),
                'info':{
                    'fields': ['symbol', 'mutual_fund_name', 'held_volume', 'change_volume', 'change_percent', 'change_value', 'outstanding_percent', 'portfolio_percent', 'time'],
                    'symbol': symbol
                }
            }
            yield d
