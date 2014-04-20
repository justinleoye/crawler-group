#coding:utf-8

from pyquery import PyQuery as pq

from pyutils import *
from quant_crawler import Crawler, Request, Response

from quant_serviced import serviced

from .utils import *

# time service.yield ,'20130930' like, date
def get_time_service(start_date=None):
    for time in get_timestring_service(start_date):
        yield time.replace('-','')

class PublicFundListCrawler(Crawler):
    def process_response(self, request, response, crawler):
        info = request['info']
        if not info['is_fund_list_page']:
            return

        text = response.content
        #print repr(text)
        html = pq(text)
        #print repr(html)
        div = html('div[class="result_list"]')
        tbody = div('table')('tbody')
        #print repr(tbody)
        assert tbody

        params = {
            'time':'20131231',
            'fund_id': '163412'
        }
        for tr in tbody.find('tr'):
            tr = pq(tr)
            params['fund_id'] = tr('td').eq(2)('a').html()

            for time in get_time_service('2010-03-31'):
                params['time'] = time
                url = 'http://www.howbuy.com/fund/%(fund_id)s/zccg/?date=%(time)s' % params
                target = '%s/%s/%s' % (info['job_cache_path'], params['fund_id'], time)
                task_id = '%s%s' % (params['fund_id'], time)
                info = {
                    'fields': ['fund_id', 'time', 'order', 'symbol', 'name', 'hold_volume', 'hold_value', 'hold_percent', 'hold_volume_change'],
                    'fund_id': params['fund_id'],
                    'time': time,
                    'job_cache_path': info['job_cache_path'],
                    'qd': info['qd'],
                    'is_fund_list_page': False
                }
                yield Request(url=url, target=target, task_id=task_id, info=info)

        for textarea in div.find('textarea'):
            textarea = pq(textarea)
            trs = pq(textarea.html())
            for tr in trs.find('tr'):
                tr = pq(tr)
                params['fund_id'] = tr('td').eq(2)('a').html()

                for time in get_time_service('2010-03-31'):
                    params['time'] = time
                    url = 'http://www.howbuy.com/fund/%(fund_id)s/zccg/?date=%(time)s' % params
                    target = '%s/%s/%s' % (info['job_cache_path'], params['fund_id'], time)
                    task_id = '%s%s' % (params['fund_id'], time)
                    info = {
                        'fields': ['fund_id', 'time', 'order', 'symbol', 'name', 'hold_volume', 'hold_value', 'hold_percent', 'hold_volume_change'],
                        'fund_id': params['fund_id'],
                        'time': time,
                        'job_cache_path': info['job_cache_path'],
                        'qd': info['qd'],
                        'is_fund_list_page': False
                    }
                    yield Request(url=url, target=target, task_id=task_id, info=info)

    def filter(self, request, response):
        info = request['info']
        fields = info['fields']

        if info['is_fund_list_page']:
            text = response.content
            #print repr(text)
            html = pq(text)
            #print repr(html)
            div = html('div[class="result_list"]')
            tbody = div('table')('tbody')
            #print '+++++++++++++++++++++++++++++++++++++++++++++++'
            #print repr(tbody)
            assert tbody

            for tr in tbody.find('tr'):
                tr = pq(tr)
                d = {
                    fields[0]: tr('td').eq(2)('a').html(),
                    fields[1]: tr('td').eq(3)('a').html()
                }
                yield {'t1': d}

            for textarea in div.find('textarea'):
                textarea = pq(textarea)
                trs = pq(textarea.html())
                for tr in trs.find('tr'):
                    tr = pq(tr)
                    d = {
                        fields[0]: tr('td').eq(2)('a').html(),
                        fields[1]: tr('td').eq(3)('a').html()
                    }
                    yield {'t1': d}
        else:
            qd = info['qd']
            qd_client = serviced.get_service_client('quant_data.%s' % qd)

            text = response.content
            div = pq(text)('div[class="part_g"]')
            assert div
            table = div('table').eq(0)
            assert table
            #print repr(table)
            #print table
            for tr in table.find('tr')[2::]:
                tr = pq(tr)
                d = {
                    fields[0]: info['fund_id'],
                    fields[1]: info['time'],
                    fields[2]: num_normalize(tr('td').eq(0).html()),
                    fields[3]: qd_client.normalize_symbol(tr('td').eq(1).html()),
                    fields[4]: tr('td').eq(2).html(),
                    fields[5]: volume_normalize(float_normalize(tr('td').eq(3).html())),
                    fields[6]: value_normalize(float_normalize(tr('td').eq(4).html()),'w'),
                    fields[7]: percent_normalize(float_normalize(tr('td').eq(5).html().replace('%', ''))),
                    fields[8]: volume_normalize(float_normalize(tr('td').eq(6)('span').html())),
                }
                yield {'t2': d}



    def tasks(self, job):
        qd = job.get('quant_data')

        url = 'http://www.howbuy.com/fund/fundranking/'

        d = {
            'url': url,
            'target': '%s/fundlist' % (job['cache_path']),
            'task_id': 'fundlist',
            'info': {
                'fields': ['fund_id', 'fund_name'],
                'qd': qd,
                'is_fund_list_page': True,
                'job_cache_path': job['cache_path']
            }
        }
        yield d

