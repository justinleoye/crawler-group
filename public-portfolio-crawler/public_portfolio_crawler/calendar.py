#coding: utf-8

from pyquery import PyQuery as pq

from pyutils import *
from quant_serviced import serviced
from quant_crawler import Crawler

from .utils import *

import datetime
import re

RANGE_RE = re.compile(r'.+-[^)].+')
RANGE_LEFT_RE = re.compile(r'.+-')
RANGE_SUB_RE = re.compile(r'.+-')

HOUR_MINUTE_RE = re.compile(r'\d{2}:\d{2}')

def mixed_figure_classify(s):
    range_left = None
    range_right = None
    not_range = None
    mark = None
    if not s:
        return (None,None,None,None)
    if RANGE_RE.match(s):
        m = RANGE_LEFT_RE.match(s)
        left = m.group(0)[0:-1]
        right = RANGE_SUB_RE.sub('',s,1)
        range_left,mark = mixed_figure_str_noramlize(left)
        range_right,mark = mixed_figure_str_noramlize(right)
    else:
        not_range,mark = mixed_figure_str_noramlize(s)
    return (not_range,range_left,range_right,mark)

def mixed_figure_str_noramlize(s):
    if not s:
        return (None,None)
    weight = 1
    mark = ''
    s.strip()

    #print 'the s in func:',s
    #strip the end of sting
    try:
        while s[-1] not in '1234567890%KMBT':
            s = s[0:-1]
    except IndexError,e:
        print e
        return (None,None)

    #normalize the feagure
    if s.endswith('%'):
        weight = 0.01
        s = s[0:-1]
        mark='percent'
    if s.endswith('/5'):
        weight = 0.01
        s = s[0:-2]
        mark='percent'
    if s.endswith('K'):
        weight = 1000
        s = s[0:-1]
    if s.endswith('M'):
        weight = 1000000
        s = s[0:-1]
    if s.endswith('B'):
        weight = 1000000000
        s = s[0:-1]
    if s.endswith('T'):
        weight = 1000000000000
        s = s[0:-1]

    #find and mark the currency
    if s.find(u'A$') >= 0:
        s = s.replace(u'A$','')
        mark = u'A$'
    elif s.find(u'$A') >= 0:
        s = s.replace(u'$A','')
        mark = u'A$'
    elif s.find(u'HK$') >= 0:
        s = s.replace(u'HK$','')
        mark = u'HK$'
    elif s.find(u'NZ$') >= 0:
        s = s.replace(u'NZ$','')
        mark = u'NZ$'
    elif s.find(u'S$') >= 0:
        s = s.replace(u'S$','')
        mark = u'S$'
    elif s.find(u'Can$') >= 0:
        s = s.replace(u'Can$','')
        mark = u'Can$'
    elif s.find(u'C$') >= 0:
        s = s.replace(u'C$','')
        mark = u'Can$'
    elif s.find(u'$') >= 0:
        s = s.replace(u'$', '')
        mark = u'$'
    if s.find(u'¥') >= 0:
        s = s.replace(u'¥','')
        mark = u'¥'
    if s.find(u'£') >= 0:
        s = s.replace(u'£','')
        mark = u'£'
    if s.find(u'€') >= 0:
        s = s.replace(u'€','')
        mark = u'€'

    #fix the float number
    s = fix_float_string_format(s)

    print 's in func:',repr(s)
    #strip the end of sting, make sure s is a figure
    try:
        while s[-1] not in '1234567890':
            s = s[0:-1]
    except IndexError,e:
        print e
        return (None,None)
    print 's in func before float_normalize:',repr(s)
    s = float_normalize(s)
    print 's:',s
    s = s * weight
    return (s,mark)


def get_week_service(start, end):
    #args:
    #   start --> like '2013-02-11'
    #   end --> like '2014-02-11'
    start = datetime.datetime.strptime(start,'%Y-%m-%d')
    end = datetime.datetime.strptime(end,'%Y-%m-%d')
    today = datetime.datetime.now()
    if end > today:
        end = today

    weekday_start = start.isocalendar()[2]
    start_week_day = start + datetime.timedelta(days= 0 - weekday_start)
    weekday_end = end.isocalendar()[2]
    end_week_day = end + datetime.timedelta(days= 0 - weekday_end)

    while start_week_day <= end_week_day:
        yield start_week_day
        start_week_day = start_week_day + datetime.timedelta(days=7)

class PublicCalendarENCrawler(Crawler):
    def filter(self, request, response):
        info = request['info']
        fields = info['fields']

        text = response.content
        text = text.replace('\n','')
        if not isinstance(text,unicode):
            print 'trans into unicode'
            text = text.decode('utf-8')
        table = pq(text)('#e-cal-table')
        
        weekday = ''
        for tr in table.find('tr')[1::]:
            tr = pq(tr)
            
            if tr('td').eq(0)('span'):
                w_text = tr('td').eq(0)('span').html()
                weekday = w_text.split('<br>')[1] if w_text.find('<br>') >= 0 else w_text.split('<br />')[1]
                weekday = weekday.strip()
                print weekday

            if not tr('td').eq(2)('div'):
                continue
            time = tr('td').eq(1).html() if tr('td').eq(1).html() else u'00:00'
            r = HOUR_MINUTE_RE.search(time)
            time = r.group(0) if r else u'00:00'
            print time
            real_time = info['year']+ ' '+weekday+ ' ' + time 
            real_time = real_time.strip()
            real_time = datetime.datetime.strptime(real_time,'%Y %b %d %H:%M')
            print 'real_time:',repr(real_time)
            #real_time.astimezone()
            print real_time.tzinfo
            currency = tr('td').eq(2)('div').attr('class').split('-')[2]
            print 'currency:',currency
            event = tr('td').eq(3).html()
            importance = tr('td').eq(4).attr('class').split(' ',1)[1].strip() if tr('td').eq(4).attr('class') else None
            print 'importance:',importance
            print tr('td').eq(5)('span').html()
            actual = tr('td').eq(5)('span').html() if tr('td').eq(5)('span') else tr('td').eq(5).html()
            forecast = tr('td').eq(6)('span').html() if tr('td').eq(6)('span') else tr('td').eq(6).html()
            previous = tr('td').eq(7)('span').html() if tr('td').eq(7)('span') else tr('td').eq(7).html()
            print 'actual:',actual
            print 'forecast:',forecast
            print 'previous:',previous
            normalized_actual,actual_range_left,actual_range_right,actual_mark = mixed_figure_classify(actual)
            normalized_forecast,forecast_range_left,forecast_range_right,forecast_mark = mixed_figure_classify(forecast)
            normalized_previous,previous_range_left,previous_range_right,previous_mark = mixed_figure_classify(previous)
            print 'actual_range_left:',actual_range_left
            print 'actual_range_right:',actual_range_right
            print 'forecast_range_left:',forecast_range_left
            print 'forecast_range_right:',forecast_range_right
            print 'previous_range_right:',previous_range_left
            print 'previous_range_right:',previous_range_right

            d = {
                fields[0]: real_time,
                fields[1]: currency,
                fields[2]: event,
                fields[3]: importance,
                fields[4]: actual,
                fields[5]: forecast,
                fields[6]: previous,
                fields[7]: normalized_actual,
                fields[8]: normalized_forecast,
                fields[9]: normalized_previous,
                fields[10]: actual_range_left,
                fields[11]: actual_range_right,
                fields[12]: forecast_range_left,
                fields[13]: forecast_range_right,
                fields[14]: previous_range_left,
                fields[15]: previous_range_right,
                fields[16]: actual_mark,
                fields[17]: forecast_mark,
                fields[18]: previous_mark,
            }
            yield d



    def tasks(self, job):
        qd = job.get('quant_data')

        params = {
            'time_zone': '0',
            'week': 'today',
            'filter': '&eur=true&usd=true&jpy=true&gbp=true&chf=true&aud=true&cad=true&nzd=true&cny=true&high=true&medium=true&low=true'
        }
        for week in get_week_service('2010-01-20','2014-02-23'):
            url_week = week.strftime('%Y/%m%d')
            params['week'] = url_week
            url = 'http://www.dailyfx.com/calendar?tz=%(time_zone)s&sort=date&week=%(week)s%(filter)s' % params

            d = {
                'url': url,
                'target': '/%s/%s' % (job['cache_path'], url_week),
                'task_id': '%s' % (url_week),
                'info': {
                    'fields': ['time', 'currency', 'event', 'importance', 'actual', 'forecast', 'previous', 'normalized_actual', 'normalized_forecast', 'normalized_previous', 'actual_range_left', 'actual_range_right', 'forecast_range_left', 'forecast_range_right', 'previous_range_left', 'previous_range_right', 'actual_mark', 'forecast_mark', 'previous_mark'],
                    'year': week.strftime('%Y')
                }
            }
            yield d
