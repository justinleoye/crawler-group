#coding: utf-8

from pyquery import PyQuery as pq
import json

from pyutils import *
from quant_crawler import Crawler
from quant_serviced import serviced

from .utils import *

class PublicSymbolListUSCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']

        text = response.content
        div = pq(text)('#ctl00_cph1_divSymbols')
        table = pq(div)('table')
        assert table
        # write symbol list into json file
        # dump the symbol info into json file
        #f = open('symbol_us.json','r')
        #f_text = f.read()
        #try:
        #    f_json = json.loads(f_text)
        #except ValueError,e:
        #    print e
        #    f_json = {}
        #f.close()

        for item in table.find('tr')[1::]:
            item = pq(item)

            d = {
                fields[0]: item('td').eq(0)('a').html(),
                fields[1]: item('td').eq(1).html(),
                fields[2]: info['exchange']
            }
            print repr(d)
            # write symbol list into json file
            #if not f_json.has_key(d['symbol']) and d['exchange'] in ['AMEX','NASDAQ','NYSE']:
            #    f_json[d['symbol']] = d
            yield d
        # write symbol list into json file
        #f = open('symbol_us.json','w')
        #f.write(json.dumps(f_json))
        #f.close()

    def tasks(self, job):
        print '+++++++++++publicSymbolListUS++++++++++++++++++++'

        STOCK_EXCHANGE_LIST = ['AMEX', 'AMS', 'ASX', 'BRU', 'CBOT', 'CFE', 'CME', 'COMEX', 'EUREX', 'FOREX', 'HKEX', 'INDEX', 'KCBT', 'LIFFE', 'LIS', 'LSE', 'MGEX', 'MLSE', 'MSE', 'NASDAQ', 'NYBOT', 'NYMEX', 'NYSE', 'NZX', 'OPRA', 'OTCBB', 'PAR', 'SGX', 'TSX', 'TSXV', 'USMF', 'WCE']
        for exchange in STOCK_EXCHANGE_LIST:
        # write symbol list into json file
        #for exchange in ['AMEX', 'NASDAQ', 'NYSE']:
            for letter in EXCHANGE_LETTER_DICT[exchange]:
                params = {
                    'exchange': exchange,
                    'letter': letter
                }

                url = 'http://eoddata.com/stocklist/%(exchange)s/%(letter)s.htm' % params

                d = {
                    'url': url,
                    'target': '%s/%s/%s' % (job['cache_path'], exchange, letter),
                    'task_id': '%s%s' % (exchange, letter),
                    'info': {
                        'fields': ['symbol', 'name', 'exchange'],
                        'exchange': exchange,
                    }
                }
                yield d

EXCHANGE_LETTER_DICT = {'INDEX': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Z'], 'PAR': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'X', 'Z'], 'FOREX': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'X', 'Z'], 'CME': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'W', 'X'], 'LIFFE': ['A', 'C', 'E', 'F', 'G', 'I', 'J', 'L', 'Q', 'R', 'S', 'V', 'X', 'Y'], 'AMEX': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], 'TSX': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], 'LIS': ['A', 'B', 'C', 'E', 'F', 'G', 'I', 'J', 'L', 'M', 'N', 'P', 'R', 'S', 'T', 'V', 'Z'], 'USMF': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], 'MSE': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'J', 'L', 'M', 'N', 'P', 'R', 'S', 'T', 'U', 'V', 'Z'], 'CBOT': ['A', 'B', 'C', 'D', 'E', 'F', 'J', 'O', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], 'SGX': ['3', '5', '6', '7', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'i', 'J', 'k', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], 'LSE': ['0', '1', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], 'OTCBB': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], 'OPRA': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], 'ASX': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], 'TSXV': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], 'MGEX': ['A', 'D', 'I', 'M', 'N'], 'MLSE': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'J', 'L', 'M', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'Z'], 'AMS': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'Y', 'Z'], 'NZX': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Z'], 'NYBOT': ['A', 'C', 'D', 'E', 'G', 'H', 'J', 'K', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'Y', 'Z'], 'NASDAQ': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], 'WCE': ['A', 'B', 'D', 'M', 'R', 'W'], 'COMEX': ['G', 'H', 'Q', 'S', 'V', 'Y'], 'NYSE': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], 'HKEX': ['0', '1', '2', '3', '6', '8'], 'BRU': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'Z'], 'CFE': ['Q', 'R', 'V', 'W'], 'EUREX': ['A', 'C', 'D', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'O', 'P', 'Q', 'S', 'T', 'W'], 'NYMEX': ['B', 'C', 'D', 'F', 'H', 'J', 'K', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X'], 'KCBT': ['K', 'M']}
