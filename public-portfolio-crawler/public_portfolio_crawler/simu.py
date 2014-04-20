#coding:utf-8

import math
import json
import copy
from datetime import datetime
from pyquery import PyQuery as pq

from pyutils import *
from quant_crawler import Crawler, Request, Response

from quant_serviced import serviced

from .utils import *


def get_simuhold_symbols(timestring):
    #fake func here
    for i in ['002224', '002595', '002070']:
        yield i

class PublicSimuMainHoldCrawler(Crawler):
    def process_response(self, request, response, crawler):
        info = request['info']

        if info['mainhold']:
            text = response.content
            data_json = json.loads(text)
            
            if data_json.has_key('data'):
                if data_json['data']:
                    for item in data_json['data']:
                        symbol = item['sec_code']
                        params = {
                            'time': info['time'],
                            'page_size': '20',
                            'page_index': 1,
                            'symbol': symbol
                        }
                        url = 'http://dc.simuwang.com/api/api_mainhold.php?condition=inception_year:%(time)s;sec_code:%(symbol)s;default:1;sort_name:holding_ratio;sort_asc:desc;&mainhold_type=2&page_size=%(page_size)s&page_index=%(page_index)s' % params
                        target = '%s/%s/%s' % (info['job_cache_path'], info['time'], symbol)
                        task_id = '%s%s' % (info['time'],symbol)
                        info_new = copy.deepcopy(info)
                        info_new['mainhold'] = False
                        info_new['symbol'] = symbol

                        yield Request(url=url, target=target, info=info_new, encoding=request.encoding, task_id=task_id)

    def filter(self, request, response):
        info = request['info']
        time = info['time']
        qd = info['qd']
        #qd_client = serviced.get_service_client('quant_data.%s' % qd)

        text = response.content

        data_json = json.loads(text)
        #print repr(data_json)
        if data_json.has_key('data'):
            if data_json['data']:
                for item in data_json['data']:
                    if info['mainhold']:
                        fields = info['fields_1']
                        d = {
                            'time': date_normalize(time, '%Y-%m-%d'),
                            fields[0]: item['id'],
                            fields[1]: datetime_utils.str_to_datetime(item['portfolio_date']),
                            fields[2]: item['stock_name'],
                            #fields[3]: qd_client.normalize_symbol(item['sec_code']) if item['sec_code'] else None,
                            fields[3]: item['sec_code'],
                            fields[4]: num_normalize(item['curr_fund_cnts']),
                            fields[5]: volume_normalize(float_normalize(item['curr_holding_num'])),
                            fields[6]: percent_normalize(float_normalize(item['curr_holding_ratio'])),
                            fields[7]: num_normalize(item['pre_fund_cnts']),
                            fields[8]: volume_normalize(float_normalize(item['pre_holding_num'])),
                            fields[9]: percent_normalize(float_normalize(item['pre_holding_ratio'])),
                            fields[10]: volume_normalize(float_normalize(item['holding_num_change'])),
                            fields[11]: percent_normalize(float_normalize(item['holding_ratio_change'])),
                            fields[12]: item['max_holding_fund_short_name'],
                            fields[13]: item['max_holding_fund_id'],
                            fields[14]: volume_normalize(float_normalize(item['max_holding_num_fund'])),
                            fields[15]: percent_normalize(float_normalize(item['max_holding_ratio_fund']))
                        }
                        yield {'t1': d}
                    else:
                        symbol = info['symbol']
                        fields = info['fields_2']
                        d = {
                            'time': date_normalize(time, '%Y-%m-%d'),
                            #'symbol': qd_client.normalize_symbol(symbol),
                            'symbol': symbol,
                            fields[0]: item['id'],
                            fields[1]: item['fund_name'],
                            fields[2]: item['fund_short_name'],
                            fields[3]: item['fund_id'],
                            fields[4]: item['company_short_name'],
                            fields[5]: item['advisor_id'],
                            fields[6]: item['mangers_name'],
                            fields[7]: item['managers_id'],
                            fields[8]: volume_normalize(item['holding_num']),
                            fields[9]: percent_normalize(item['holding_ratio']),
                            fields[10]: volume_normalize(item['pre_holding_num']),
                            fields[11]: percent_normalize(item['pre_holding_ratio']),
                            fields[12]: volume_normalize(item['holding_num_change']),
                            fields[13]: percent_normalize(item['holding_ratio_change']),
                            fields[14]: item['max_holding_stock_name'],
                            fields[15]: percent_normalize(item['max_holding_ratio']),
                            #fields[16]: qd_client.normalize_symbol(item['from_code']) if item['from_code'] else None,
                            fields[16]: item['from_code'],
                            fields[17]: item['from_name'],
                            fields[18]: item['company_name'],
                            #fields[19]: qd_client.normalize_symbol(item['max_holding_sec_code']) if item['max_holding_sec_code'] else None,
                            fields[19]: item['max_holding_sec_code'],
                            fields[20]: volume_normalize(item['max_holding']),
                        }
                        yield {'t2': d}

            else:
                yield {}
        else:
            yield {}




    def tasks(self, job):
        print '++++++++++++++publicSimu++++++++++++++++++++++++'
        print repr(job)
        qd = job.get('quant_data')
        #qd.normalize_symbol()

        for time in get_timestring_service('2012-09-30'):
            params = {
                'time': time,
                'page_size':'2',
                'page_index': 1
            }

            for page_index in xrange(1,183):
                params['page_index'] = page_index

                url = 'http://dc.simuwang.com/api/api_mainhold.php?condition=inception_year:%(time)s;sort_name:curr_holding_ratio;sort_asc:desc;&mainhold_type=1&page_size=%(page_size)s&page_index=%(page_index)s' % params

                d = {
                    'url': url,
                    'target': '%s/%s/%s' % (job['cache_path'], time, page_index),
                    'task_id': '%s_%s' % (time, page_index),
                    'info': {
                        'fields_1': ['simu_zhongcang_order', 'time', 'name', 'symbol', 'curr_fund_cnts', 'curr_holding_num', 'curr_holding_ratio', 'pre_fund_cnts', 'pre_holding_num', 'pre_holding_ratio', 'holding_num_change', 'holding_ratio_change', 'max_holding_fund_name', 'max_holding_fund_id', 'max_holding_num_fund', 'max_holding_ratio_fund'],
                        'fields_2': ['simu_zhongcang_order', 'fund_name', 'fund_short_name', 'fund_id', 'company_short_name', 'advisor_id', 'managers_name', 'managers_id', 'holding_num', 'holding_ratio', 'pre_holding_num', 'pre_holding_ratio', 'holding_num_change', 'holding_ratio_change', 'max_holding_name', 'max_holding_ratio', 'from_symbol', 'from_name', 'company_name', 'max_holding_symbol', 'max_holding'],
                        'qd': qd,
                        'time': time,
                        'mainhold': True,
                        'job_cache_path': job['cache_path'],
                    }
                }
                yield d


##
# will not be used
##
class PublicSimuHoldCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']
        time = info['time']
        symbol = info['symbol']
        qd = info['qd']
        qd_client = serviced.get_service_client('quant_data.%s' % qd)

        text = response.content

        data_json = json.loads(text)
        print repr(data_json)
        if data_json.has_key('data'):
            if data_json['data']:
                for item in data_json['data']:
                    d = {
                        'time': date_normalize(time, '%Y-%m-%d'),
                        'symbol': qd_client.normalize_symbol(symbol),
                        #'symbol': symbol,
                        fields[0]: item['id'],
                        fields[1]: item['fund_name'],
                        fields[2]: item['fund_short_name'],
                        fields[3]: item['fund_id'],
                        fields[4]: item['company_short_name'],
                        fields[5]: item['advisor_id'],
                        fields[6]: item['mangers_name'],
                        fields[7]: item['managers_id'],
                        fields[8]: volume_normalize(item['holding_num']),
                        fields[9]: percent_normalize(item['holding_ratio']),
                        fields[10]: volume_normalize(item['pre_holding_num']),
                        fields[11]: percent_normalize(item['pre_holding_ratio']),
                        fields[12]: volume_normalize(item['holding_num_change']),
                        fields[13]: percent_normalize(item['holding_ratio_change']),
                        fields[14]: item['max_holding_stock_name'],
                        fields[15]: percent_normalize(item['max_holding_ratio']),
                        fields[16]: qd_client.normalize_symbol(item['from_code']) if item['from_code'] else None,
                        #fields[16]: item['from_code'],
                        fields[17]: item['from_name'],
                        fields[18]: item['company_name'],
                        fields[19]: qd_client.normalize_symbol(item['max_holding_sec_code']),
                        #fields[19]: item['max_holding_sec_code'],
                        fields[20]: volume_normalize(item['max_holding']),
                    }
                    yield d
            else:
                yield {}
        else:
            yield {}


    def tasks(self, job):
        print '+++++++++++++++++++++++++publicSimuHold+++++++++++++++++++++++++++++'
        print repr(job)
        qd = job.get('quant_data')

        for time in get_timestring_service('2012-09-30'):
            params = {
                'time': time,
                'page_size': '20',
                'page_index': 1,
                'symbol': '002595'
            }
            #here is the func return the symbols which involve the simuholding maters
            for symbol in get_simuhold_symbols(time):
                params['symbol'] = symbol
                url = 'http://dc.simuwang.com/api/api_mainhold.php?condition=inception_year:%(time)s;sec_code:%(symbol)s;default:1;sort_name:holding_ratio;sort_asc:desc;&mainhold_type=2&page_size=%(page_size)s&page_index=%(page_index)s' % params

                d = {
                    'url': url,
                    'target': '%s/%s/%s' % (job['cache_path'], time, symbol),
                    'task_id': '%s%s' % (time, symbol),
                    'info': {
                        'fields': ['simu_zhongcang_order', 'fund_name', 'fund_short_name', 'fund_id', 'company_short_name', 'advisor_id', 'managers_name', 'managers_id', 'holding_num', 'holding_ratio', 'pre_holding_num', 'pre_holding_ratio', 'holding_num_change', 'holding_ratio_change', 'max_holding_name', 'max_holding_ratio', 'from_symbol', 'from_name', 'company_name', 'max_holding_symbol', 'max_holding'],
                        'qd': qd,
                        'time': time,
                        'symbol': symbol
                    }
                }
                yield d


class PublicSimuAdvisorCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']

        data_json = json.loads(response.content)

        #print '************************'
        #print repr(data_json['data'])
        #print repr(data_json)
        #print '************************'
        if data_json.has_key('data'):
            if data_json['data']:
                for item in data_json['data']:
                    d = {
                        fields[0]: date_normalize(item['end_date'],'%Y-%m'),
                        fields[1]: item['company_id'],
                        fields[2]: item['company_name'],
                        fields[3]: item['company_short_name'],
                        fields[4]: date_normalize(item['establish_date'],'%Y-%m-%d'),
                        fields[5]: item['key_figure_id'],
                        fields[6]: item['key_figure'],
                        fields[7]: item['city'],
                        fields[8]: item['manage_cnts'],
                        fields[9]: item['fund_id'],
                        fields[10]: item['fund_short_name'],
                        fields[11]: item['fund_type'],
                        fields[12]: item['strategy'],
                        fields[13]: item['fund_status'],
                        fields[14]: item['rating_1y'],
                        fields[15]: item['rating_2y'],
                        fields[16]: item['rating_3y'],
                        fields[17]: item['ret_1y'],
                        fields[18]: item['ret_2y'],
                        fields[19]: item['ret_3y'],
                        fields[20]: item['absrank_ret_1y'],
                        fields[21]: item['fund_managers_id'],
                        fields[22]: item['nav'],
                        fields[23]: date_normalize(item['price_date'], '%Y-%m-%d'),
                        fields[24]: item['ret_1m'],
                        fields[25]: item['company_type'],
                        fields[26]: datetime_utils.str_to_datetime(item['updatetime']),
                        fields[27]: item['isvalid'],
                    }
                    yield d
            else:
                yield {}
        else:
            yield {}

    def tasks(self, job):
        print '+++++++++++++++++++publicSimuAdvisor++++++++++++++++++++++++++++'
        qd = job.get('quant_data')

        params = {
            'sort_name': 'manage_cnts',
            'sort_asc': 'desc',
            'fund_type_id': '2,4,13,14,15,16,5,9,11,17,10,7',
            'page_size': '20',
            'page_index': 1
        }
        for page_index in xrange(1,26):
            params['page_index'] = page_index
            url = 'http://dc.simuwang.com/api/api_advisor.php?condition=sort_name:%(sort_name)s;sort_asc:%(sort_asc)s;fund_type_id:%(fund_type_id)s;&page_size=%(page_size)s&page_index=%(page_index)s' % params

            d = {
                'url': url,
                'target': '%s/%s' % (job['cache_path'], page_index),
                'task_id': '%s' % (page_index),
                'info': {
                    'fields': ['end_date', 'company_id', 'company_name', 'company_short_name', 'establish_date', 'key_figure_id', 'key_figure', 'city', 'manage_cnts', 'fund_id', 'fund_short_name', 'fund_type', 'strategy', 'fund_status', 'rating_1y', 'rating_2y', 'rating_3y', 'ret_1y', 'ret_2y', 'ret_3y', 'absrank_ret_1y', 'fund_managers_id', 'nav', 'price_date', 'ret_1m', 'company_type', 'updatetime', 'isvalid'],
                    'qd': qd,
                }
            }
            yield d


class PublicSimuImCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']

        data_json = json.loads(response.content)

        if data_json.has_key('data'):
            if data_json['data']:
                for item in data_json['data']:
                    d = {
                        fields[0]: date_normalize(item['end_date'], '%Y-%m'),
                        fields[1]: item['fund_manager_id'],
                        fields[2]: item['personnel_name'],
                        fields[3]: item['company_id'],
                        fields[4]: item['company_name'],
                        fields[5]: item['company_short_name'],
                        fields[6]: item['city'],
                        fields[7]: item['profession_background'],
                        fields[8]: item['manger_cnts'],
                        fields[9]: item['fund_id'],
                        fields[10]: item['fund_name'],
                        fields[11]: item['ret_1y'],
                        fields[12]: item['absrank_ret_1y'],
                        fields[13]: item['strategy'],
                        fields[14]: item['strategy_name'],
                        fields[15]: item['fund_type'],
                        fields[16]: item['fund_type_name'],
                        fields[17]: item['fund_status'],
                        fields[18]: item['rating_2y'],
                        fields[19]: item['rating_3y'],
                        fields[20]: item['ret_2y'],
                        fields[21]: item['ret_3y'],
                        fields[22]: item['ret_1m'],
                        fields[23]: item['nav'],
                        fields[24]: date_normalize(item['price_date'],'%Y-%m-%d'),
                        fields[25]: item['fund_short_name'],
                        fields[26]: item['rating_1y'],
                        fields[27]: item['fund_status_name'],
                        fields[28]: item['company_type'],
                        fields[29]: datetime_utils.str_to_datetime(item['createtime']),
                        fields[30]: datetime_utils.str_to_datetime(item['updatetime']),
                        fields[31]: item['isvalid'],
                    }
                    yield d
            else:
                yield {}
        else:
            yield {}


    def tasks(self, job):
        params = {
            'sort_name': 'manger_cnts',
            'sort_asc': 'desc',
            'page_index':1,
            'page_size': '20',
        }
        
        for page_index in xrange(1,9):
            params['page_index'] = page_index
            url = 'http://dc.simuwang.com/api/api_im.php?page_index=%(page_index)s&page_size=%(page_size)s&sort_asc=%(sort_asc)s&sort_name=%(sort_name)s' % params

            d = {
                'url': url,
                'target': '%s/%s' % (job['cache_path'], page_index),
                'task_id': '%s' % (page_index),
                'info': {
                    'fields': ['end_date', 'fund_manager_id', 'personnel_name', 'company_id', 'company_name', 'company_short_name', 'city', 'profession_background', 'manage_cnts', 'fund_id', 'fund_name', 'ret_1y', 'absrank_ret_1y', 'strategy', 'strategy_name', 'fund_type', 'fund_type_name', 'fund_status', 'rating_2y', 'rating_3y', 'ret_2y', 'ret_3y', 'ret_1m', 'nav', 'price_date', 'fund_short_name', 'rating_1y', 'fund_status_name', 'company_type', 'createtime', 'updatetime', 'isvalid']
                }
            }
            yield d

class PublicSimuPepCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']

        data_json = json.loads(response.content)

        if data_json.has_key('data'):
            if data_json['data']:
                for item in data_json['data']:
                    d = {
                        fields[0]: item['id'],
                        fields[1]: item['fund_id'],
                        fields[2]: item['fund_status_id'],
                        fields[3]: item['fund_status'],
                        fields[4]: item['strategy_id'],
                        fields[5]: item['strategy'],
                        fields[6]: item['substrategy'],
                        fields[7]: item['substrategy_id'],
                        fields[8]: item['fund_type_id'],
                        fields[9]: item['fund_type'],
                        fields[10]: item['city'],
                        fields[11]: item['fund_short_name'],
                        fields[12]: item['managers_id'],
                        fields[13]: item['managers'],
                        fields[14]: date_normalize(item['inception_year'], '%Y'),
                        fields[15]: item['advisor_id'],
                        fields[16]: item['advisor'],
                        fields[17]: datetime_utils.str_to_datetime(item['inception_date']),
                        fields[18]: item['initial_size'],
                        fields[19]: item['futures_type'],
                        fields[20]: date_normalize(item['end_date'], '%Y-%m'),
                        fields[21]: item['ret_ytd'],
                        fields[22]: item['nav'],
                        fields[23]: item['pre_nav'],
                        fields[24]: date_normalize(item['liquidate_date']),
                        fields[25]: item['ret_incep'],
                        fields[26]: item['futures_type_id'],
                        fields[27]: item['isvisible'],
                        fields[28]: item['isvalid'],
                    }
                    yield d
            else:
                yield {}
        else:
            yield {}

    def tasks(self, job):
        params = {
            'fund_status': 2,
            'fund_type_id': '2,4,13,14,15,16,5,9,11,17,10,7',
            'page_index': 1,
            'page_size': '20',
            'sort_name': 'inception_date',
            'sort_asc': '0'
        }
        for page_index in xrange(1,224):
            params['page_index'] = page_index
            url = 'http://dc.simuwang.com/api/api_pep.php?fund_status=%(fund_status)s&fund_type_id=%(fund_type_id)s&page_index=%(page_index)s&page_size=%(page_size)s&sort_asc=%(sort_asc)s&sort_name=%(sort_name)s' % params

            d = {
                'url': url,
                'target': '%s/%s' % (job['cache_path'], page_index),
                'task_id': '%s' % (page_index),
                'info': {
                    'fields': ['id', 'fund_id', 'fund_status_id', 'fund_status', 'strategy_id', 'strategy', 'substrategy', 'substrategy_id', 'fund_type_id', 'fund_type', 'city', 'fund_short_name', 'managers_id', 'managers', 'inception_year', 'advisor_id', 'advisor', 'inception_date', 'initial_size', 'futures_type', 'end_date', 'ret_ytd', 'nav', 'pre_nav', 'liquidate_date', 'ret_incep', 'futures_type_id', 'isvisible', 'isvalid']
                }
            }
            yield d

