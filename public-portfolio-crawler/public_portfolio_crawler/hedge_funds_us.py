#coding: utf-8

from pyquery import PyQuery as pq
import re
import json

from pyutils import *
from quant_crawler import Crawler, Request, Response
from quant_serviced import serviced

from .utils import *
import datetime

def get_monday_string_Y_m_d(s,f='%Y-%m-%d'):
    t = datetime.datetime.strptime(s,f)
    m = get_monday_of_date(t)
    return m.strftime('%Y-%m-%d')

def get_month_first_day_string_Y_m_d(s,f='%Y-%m-%d'):
    y,m,d = s.split('-')
    d = '1'
    return y+'-'+m+'-'+d

def get_monday_of_date(t):
    weekday = t.isocalendar()[2]
    monday_date = t + datetime.timedelta(days= 0 - weekday)
    return monday_date

def get_quater_order(time):
    # time format should like '2013-03-31'
    md_dict = {
        '03-31': 1,
        '06-30': 2,
        '09-30': 3,
        '12-31': 4
    }
    y,md = time.split('-',1)
    ys = int(y) - 2001
    qs = md_dict[md]
    q = ys*4 + qs
    return q

class PublicHedgeFundsListUSCrawler(Crawler):
    def process_response(self, request, response, crawler):
        info = request['info']

        if not info['is_funds_list_page']:
            return
        text = response.content
        section = pq(text)('.section').eq(0)
        assert section

        params = {
            'time': '2013-09-30',
            'insider_monkey_id': '150'
        }
        ID_RE = re.compile(r'\/([0-9]+)\/')
        #count = 0
        

        for item in section('div[class="fund"]'):
            #count += 1
            #if count >=20:
            #    break
            item = pq(item)
            #print item.html()
            fund_name,managers = item('a').html().split(' - ',1)
            managers = managers.split(' And ')
            id_list = ID_RE.findall(item('a').attr('href'))
            assert id_list
            insider_monkey_id = id_list[0] if len(id_list) >= 1 else None
            params['insider_monkey_id'] = insider_monkey_id 
            
            for time in get_timestring_service('2010-12-31'):
                params['time'] = time
                url = 'http://www.insidermonkey.com/get_fund_holdings.php?hfid=%(insider_monkey_id)s&module=profile&ffp=%(time)s&fot=7&fso=1&offset=0' % params
                target = '%s/%s/%s' % (info['job_cache_path'], insider_monkey_id, time),
                task_id = '%s%s' % (insider_monkey_id, time),
                info = {
                    'fields': ['fund_name', 'time', 'order', 'security', 'symbol', 'hold_volume', 'hold_value', 'activity', 'portfolio_percent'],
                    'insider_monkey_id': insider_monkey_id,
                    'time': time,
                    'fund_name': fund_name,
                    'is_funds_list_page': False,
                    'job_cache_path': info['job_cache_path']
                }
                
                yield Request(url=url, target=target, task_id=task_id, info=info)



    def filter(self, request, response):
        info = request['info']
        fields = info['fields']

        if info['is_funds_list_page']:
            text = response.content
            section = pq(text)('.section').eq(0)
            assert section

            ID_RE = re.compile(r'\/([0-9]+)\/')

            for item in section('div[class="fund"]'):
                item = pq(item)
                #print item.html()
                name,managers = item('a').html().split(' - ',1)
                managers = managers.split(' And ')
                id_list = ID_RE.findall(item('a').attr('href'))
                insider_monkey_id = id_list[0] if len(id_list) >= 1 else None
                #print repr(managers)
                for manager in managers:
                    d = {
                        fields[0]: name,
                        fields[1]: manager,
                        fields[2]: insider_monkey_id
                    }
                    yield {'t1': d}

        else:
            text = response.content
            table = pq(text)('table[id="stock-holdings-table"]')
            assert table
            #print table
            #Because of the bug of the PyQuery,which does not work well in parsing 'tbody',so the following line's logic is wrong
            tbody = table('tbody').eq(0)
            assert tbody

            for tr in tbody.find('tr'):
                tr = pq(tr)
                order = tr('td').eq(0).html().replace('.)','')
                security = tr('td').eq(1)('a').html() if tr('td').eq(1)('a') else tr('td').eq(1)('span').html()
                symbol = tr('td').eq(2)('a').html() if tr('td').eq(2)('a') else ''
                hold_volume = tr('td').eq(3).html().replace(',','')
                hold_value = tr('td').eq(4).html().replace(',','').replace('$','')
                #print tr('td').eq(5)
                tr('td').eq(5)('img').remove()
                tr('td').eq(5)('span').remove()
                #print tr('td').eq(5)
                activity = tr('td').eq(5).html().replace('%','') if tr('td').eq(5).html() else ''
                portfolio_percent = tr('td').eq(6).html().replace('%','')
                d = {
                    fields[0]: info['fund_name'],
                    fields[1]: info['time'],
                    fields[2]: num_normalize(order),
                    fields[3]: security.strip(),
                    fields[4]: symbol.strip(),
                    fields[5]: num_normalize(hold_volume),
                    fields[6]: value_normalize(float_normalize(hold_value), 'q'),
                    fields[7]: percent_normalize(float_normalize(activity)),
                    fields[8]: percent_normalize(float_normalize(portfolio_percent)),
                }
                yield {'t2': d}


    def tasks(self, job):
        qd = job.get('quant_data')

        params = {
            'letter': 'A',
        }

        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            params['letter'] = letter
            url = 'http://www.insidermonkey.com/hedge-fund/browse/%(letter)s/' % params
            d = {
                'url': url,
                'target': '%s/%s' % (job['cache_path'], letter),
                'task_id': '%s' % (letter),
                'info': {
                    'fields': ['fund_name', 'fund_manager', 'insider_monkey_id'],
                    'is_funds_list_page': True,
                    'job_cache_path': job['cache_path']
                }
            }
            yield d

#
# will not be used
# has been changed for crawler Warren Buffet hedge data
#
class PublicHedgeFundUSCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']

        text = response.content
        table = pq(text)('table[id="stock-holdings-table"]')
        assert table
        #print table
        #Because of the bug of the PyQuery,which does not work well in parsing 'tbody',so the following line's logic is wrong
        tbody = table('tbody').eq(0)
        assert tbody

        for tr in tbody.find('tr'):
            tr = pq(tr)
            order = tr('td').eq(0).html().replace('.)','')
            security = tr('td').eq(1)('a').html() if tr('td').eq(1)('a') else tr('td').eq(1)('span').html()
            symbol = tr('td').eq(2)('a').html() if tr('td').eq(2)('a') else ''
            hold_volume = tr('td').eq(3).html().replace(',','')
            hold_value = tr('td').eq(4).html().replace(',','').replace('$','')
            #print tr('td').eq(5)
            tr('td').eq(5)('img').remove()
            tr('td').eq(5)('span').remove()
            #print tr('td').eq(5)
            activity = tr('td').eq(5).html().replace('%','') if tr('td').eq(5).html() else ''
            portfolio_percent = tr('td').eq(6).html().replace('%','')
            d = {
                fields[0]: info['fund_name'],
                fields[1]: info['time'],
                fields[2]: num_normalize(order),
                fields[3]: security.strip(),
                fields[4]: symbol.strip(),
                fields[5]: num_normalize(hold_volume),
                fields[6]: value_normalize(float_normalize(hold_value), 'q'),
                fields[7]: percent_normalize(float_normalize(activity)),
                fields[8]: percent_normalize(float_normalize(portfolio_percent)),
            }
            d_json = {
                'time': d['time'],
                'hold_volume': d['hold_volume'],
                'price': d['hold_value'] / d['hold_volume'],
                'symbol': d['symbol'],
                'change_volume': None,
                'activity': d['activity']
            }
            try:
                f = open('hedge_funds_Warren_Buffet.json','r')
                data_json = json.loads(f.read())
                f.close()
            except (IOError,ValueError),e:
                print e
                data_json = {}

            try:
                data_json[d['time']][d['symbol']] = d_json
            except KeyError,e:
                print e
                data_json[d['time']] = {}
                data_json[d['time']][d['symbol']] = d_json

            f = open('hedge_funds_Warren_Buffet.json','w')
            f.write(json.dumps(data_json))
            f.close()

            
            yield d


    def tasks(self, job):
        params = {
                'time': '2013-06-30',
                'insider_monkey_id': '150'
        }

        for insider_monkey_id in ['1']:
            params['insider_monkey_id'] = insider_monkey_id
            for time in get_timestring_service('2012-06-30'):
                params['time'] = time
                url = 'http://www.insidermonkey.com/get_fund_holdings.php?hfid=%(insider_monkey_id)s&module=profile&ffp=%(time)s&fot=7&fso=1&offset=0' % params
                d = {
                    'url': url,
                    'target': '%s/%s/%s' % (job['cache_path'], insider_monkey_id, time),
                    'task_id': '%s%s' % (insider_monkey_id, time),
                    'info': {
                        'fields': ['fund_name', 'time', 'order', 'security', 'symbol', 'hold_volume', 'hold_value', 'activity', 'portfolio_percent'],
                        'insider_monkey_id': insider_monkey_id,
                        'time': time,
                        'fund_name': 'AAAA'
                    }
                }
                yield d

#
# will not be used
# has been changed for crawler Warren Buffet hedge data
#
class PublicHedgeFundUSWhaleCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']

        text = response.content
        data_json = json.loads(text)
        if not data_json['rows']:
            yield {}

        for row in data_json['rows']:
            order = row['current_ranking']
            security = row['name']
            symbol = row['symbol']
            hold_volume = row['current_shares']
            hold_value = row['current_mv']
            activity = row['percent_shares_change']
            portfolio_percent = row['current_percent_of_portfolio']
            d = {
                fields[0]: info['fund_name'],
                fields[1]: info['time'],
                fields[2]: num_normalize(order),
                fields[3]: security.strip(),
                fields[4]: symbol.strip(),
                fields[5]: num_normalize(hold_volume),
                fields[6]: float_normalize(hold_value),
                fields[7]: percent_normalize(float_normalize(activity)),
                fields[8]: percent_normalize(float_normalize(portfolio_percent)),
            }
            print 'hold_volume:',d['hold_volume']
            print 'hold_value:',d['hold_value']
            d_json = {
                'time': d['time'],
                'hold_volume': d['hold_volume'],
                'price': d['hold_value'] / d['hold_volume'] if d['hold_volume'] != 0 else None,
                'symbol': d['symbol'],
                'change_volume': None,
                'activity': d['activity'],
                'port': d['portfolio_percent']
            }
            try:
                f = open('hedge_funds_Warren_Buffet.json','r')
                data_json = json.loads(f.read())
                f.close()
            except (IOError,ValueError),e:
                print e
                data_json = {}

            try:
                data_json[d['time']][d['symbol']] = d_json
            except KeyError,e:
                print e
                data_json[d['time']] = {}
                data_json[d['time']][d['symbol']] = d_json

            f = open('hedge_funds_Warren_Buffet.json','w')
            f.write(json.dumps(data_json))
            f.close()

            
            yield d


    def tasks(self, job):
        params = {
                'whale_id': '349',
                'q': 1
        }

        for whale_id in ['349']:
            params['whale_id'] = whale_id
            for time in get_timestring_service('2012-06-30',False):
                print 'time:',time
                q_order = get_quater_order(time)
                print 'q:',q_order
                params['q'] = q_order
                url = 'http://whalewisdom.com/filer/holdings?id=%(whale_id)s&q1=%(q)s&type_filter=1,2,3,4&symbol=&change_filter=1,2,3,4,5&minimum_ranking=&minimum_shares=&is_etf=0&_search=false&rows=100&page=1&sidx=current_ranking&sord=asc' % params
                d = {
                    'url': url,
                    'target': '%s/%s/%s' % (job['cache_path'], whale_id, time),
                    'task_id': '%s%s' % (whale_id, time),
                    'info': {
                        'fields': ['fund_name', 'time', 'order', 'security', 'symbol', 'hold_volume', 'hold_value', 'activity', 'portfolio_percent'],
                        'insider_monkey_id': whale_id,
                        'time': time,
                        'fund_name': 'AAAA'
                    }
                }
                yield d

#
# get history data from yahoo
#
class PublicStockPriceUSCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']

        text = response.content
        print repr(text)
        print response.headers['content-type']
        if response.headers['content-type'] == 'text/csv':
            print text.split('\n')
            line = text.split('\n')[1]
            print 'line:',line
            dt,open_price,high_price,low_price,close_price,volume,adj_price = line.split(',')
            d = {
                'symbol': info['symbol'],
                'date': dt,
                'close_price': close_price
            }
            print 'colse:',close_price
            f = open('hedge_funds_Warren_Buffet.json','r')
            f_json = json.loads(f.read())
            f.close()

            try:
                f_json[info['time']][info['symbol']]['price'] = close_price
            except KeyError,e:
                print e
            try:
                f = open('hedge_funds_Warren_Buffet.json','w')
                f.write(json.dumps(f_json))
                f.close()
            except IOError,e:
                print e

            yield d
        else:
            yield {}


    def tasks(self, job):
        params = {
            's_y': '2008',
            's_m': '3',#month should minus 1
            's_d': '1',
            't_y': '2009',
            't_m': '0',#month should minus 1
            't_d': '23',
            'symbol': 'GOOG'
        }

        symbol_list = []
        f = open('hedge_funds_Warren_Buffet.json','r')
        f_json = json.loads(f.read())
        f.close()
        for k,v in f_json.iteritems():
            for s,dontcare in v.iteritems():

                if s not in symbol_list:
                    symbol_list.append(s)
        print symbol_list
        for time in get_timestring_service('2012-06-30',False):
            for symbol in symbol_list:
                params['symbol'] = symbol
                print 'time:',time
                monday_date = get_month_first_day_string_Y_m_d(time)
                print 'Month firstday:',monday_date

                params['s_y'],params['s_m'],params['s_d'] = monday_date.split('-')
                params['t_y'],params['t_m'],params['t_d'] = time.split('-')
                params['s_m'] = str(int(params['s_m']) - 1)
                params['t_m'] = str(int(params['t_m']) - 1)

                print params
                url = 'http://ichart.yahoo.com/table.csv?s=%(symbol)s&a=%(s_m)s&b=%(s_d)s&c=%(s_y)s&d=%(t_m)s&e=%(t_d)s&f=%(t_y)s&g=d&ignore=.csv' % params

                d = {
                    'url': url,
                    'target': '%s/%s/%s' % (job['cache_path'], symbol, time),
                    'task_id': '%s%s' % (symbol, time),
                    'info': {
                        'fields': ['symbol', 'price', 'time'],
                        'symbol': symbol,
                        'time': time
                    }
                }
                yield d

