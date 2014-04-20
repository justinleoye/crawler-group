import re
from time import mktime
from datetime import datetime, timedelta, time, date
from dateutil.relativedelta import relativedelta
import dateutil.parser
import calendar

from pyutils import *

DATE_FMT = "%Y-%m-%d"
TIME_FMT = "%H:%M:%S"
TIME_SHORT_FMT = "%H:%M"
DATETIME_FMT = "%Y-%m-%d %H:%M:%S"
DATETIME_SHORT_FMT= "%Y-%m-%d %H:%M"
DATETIME_ISO_FMT = "%Y-%m-%dT%H:%M:%S"

LEN_DATE_STR = len('2012-01-01')
LEN_TIME_STR = len('12:00:00')
LEN_TIME_SHORT_STR = len('12:00')
LEN_DATETIME_STR = len('2012-01-01 12:00:00')
LEN_DATETIME_SHORT_STR = len('2012-01-01 12:00')

_simulated_now = None

def split_date(date):
    """
    day: 1-31
    month: 1-12
    quarter: 1-4
    >>> split_date('2010-02-28')
    {'quarter': 1, 'month': 2, 'day': 28, 'year': 2010}
    """
    a = map(int, date.split('-'))
    year = a[0]
    month = a[1]
    day = a[2]
    quarter = (month-1)/3+1
    r = { 
        'year': year, 
        'month': month, 
        'day': day, 
        'quarter': quarter 
    }
    return r
    


def get_now():
    if _simulated_now is not None:
        return _simulated_now
    else:
        return datetime.now()
    
def get_simulated_now():
    return _simulated_now

def set_now(now):
    global _simulated_now
    old = _simulated_now
    if now is not None:
        _simulated_now = get_datetime(now)
    return old


def is_date_or_datetime(x):
    return isinstance(x, (date, datetime))

def to_date(d):
    if is_date_or_datetime(d):
        return d
    else:
        a = split_date(d)
        d = date(a['year'], a['month'], a['day'])
        return d

def str_to_date(date_str):
    return to_date(date_str)

def str_to_datetime(datetime_str, fmt=None):
    if not datetime_str:
        return None

    if isinstance(datetime_str, datetime):
        return datetime_str

    if datetime_str=='now':
        return datetime.now()
    elif datetime_str=='today':
        t = datetime.now()
        return datetime(t.year, t.month, t.day)

    if fmt is None:
        return dateutil.parser.parse(datetime_str)
    else:
        r = datetime.strptime(datetime_str, fmt)
        return r

def str_to_date_or_time(datetime_str, fmt=DATETIME_FMT):
    n = len(datetime_str)
    if n<LEN_DATETIME_STR:
        if n==LEN_DATE_STR and datetime_str.find('-')>=0:
            r = datetime.strptime(datetime_str, DATE_FMT).date()

        elif n==LEN_TIME_STR:
            r = datetime.strptime(datetime_str, TIME_FMT).time()

        elif n==LEN_TIME_SHORT_STR:
            r = datetime.strptime(datetime_str, TIME_SHORT_FMT).time()

        elif n==LEN_DATETIME_SHORT_STR:
            r = datetime.strptime(datetime_str, DATETIME_SHORT_FMT)

        else:
            raise Exception("datetime_str len error, date: %s, len: %d" % (datetime_str,n))
    else:
        r = datetime.strptime(datetime_str, fmt)
    return r

def to_datetime(t):
    if t is None:
        return None
    elif isinstance(t, (date, datetime)):
        return t
    else:
        return str_to_datetime(t)

def datetime_to_str(time):
    if time is None:
        return None
    else:
        return time.strftime(DATETIME_FMT)

def date_to_str(time):
    if time is None:
        return None
    elif is_str(time):
        return time
    else:
        return time.strftime(DATE_FMT)

def datetime_to_timestamp(t):
    return int(to_datetime(t).strftime('%s'))

def datetime_to_millisecond(t):
    return int(round(mktime(t.timetuple())*1000))

def datetime_to_microsecond(t):
    return int(round(mktime(t.timetuple())*1000000)) + t.microsecond

def datetime_from_microsecond(t):
    return datetime.fromtimestamp(t/1000000).replace(microsecond=t%1000000)

def datetime_from_timestamp(t):
    return datetime.fromtimestamp(t).strftime(DATETIME_FMT)

def date_from_timestamp(sec):
    return datetime.fromtimestamp(sec).strftime(DATE_FMT)

def min_from_timestamp(sec):
    return datetime.utcfromtimestamp(sec).strftime("%s %s" % (DATE_FMT, TIME_SHORT_FMT))

def date_str_by_period(d, p):
    d = date_to_str(d)
    if p=='day' or p=='daily':
        #2012-01-01
        return d
    elif p=='week' or p=='weekly':
        #2012.W01 W:1-53
        w = week_of(s)
        return '%s.W%02d' % (d[:4], w)
    elif p=='month' or p=='monthly':
        #2012-01
        return d[:7]
    elif p=='quarter' or p=='quarterly':
        #2012.Q1  Q:1-4
        q = quarter_of(d)
        return '%s.Q%d' % (d[:4], q)
    else:
        #2012-01-01
        return d

def today():
    raise Exception("use today_str instead")
    return datetime.now().strftime('%s' % DATE_FMT)

def today_datetime():
    t = datetime.now()
    return datetime(t.year, t.month, t.day)

def today_str_by_period(p):
    return date_str_by_period(today_str(), p)

def today_str():
    return datetime.now().strftime('%s' % DATE_FMT)

def yesterday_str():
    return prev_day(today())

def yesterday():
    raise Exception("use yesterday_str")

def year_of(date):
    return split_date(date)['year']

def month_of(date):
    return split_date(date)['month']

def day_of(date):
    return split_date(date)['day']

def weekday_of(date):
    """
    #0==monday
    >>> weekday_of('2011-06-01')
    2
    >>> weekday_of('2011-05-30')
    0
    """
    return to_date(date).weekday()

def week_of(date):
    """
    #1-53
    >>> week_of('2010-06-16')
    24
    """
    return to_date(date).isocalendar()[1]
    
def quarter_of(date):
    return split_date(date)['quarter']

def timedelta_seconds(*args, **kwargs):
    d = timedelta(*args, **kwargs)
    return d.seconds + d.days * 3600 * 24
    
def date_delta(date_str, delta):
    """
    >>> date_delta('2010-02-28',1)
    '2010-03-01'
    >>> date_delta('2010-03-01',-2)
    '2010-02-27'
    """
    d = to_date(date_str) + timedelta(delta)
    return '%04d-%02d-%02d' % (d.year, d.month, d.day)
    
def prev_day(date, change=1):
    return date_delta(date, -change)

def next_day(date, change=1):
    return date_delta(date, change)

def get_time(time, default_now=True):
    if time is None:
        if default_now:
            return datetime.now()
        else:
            return None
    if is_str(time):
        return str_to_datetime(time)
    elif isinstance(time,int):
        return datetime.fromtimestamp(time)
    else:
        return time

def get_date(time):
    t = get_time(time)
    return datetime(year=t.year, month=t.month, day=t.day)

def get_datetime(t):
    if t is None:
        return None
    elif is_str(t):
        return dateutil.parser.parse(t)
    elif isinstance(t, (date, datetime, time)):
        return t
    elif isinstance(t, (int,long)):
        return datetime.fromtimestamp(t)
    else:
        return t

def ago(time, *args, **kwargs):
    return get_time(time) - timedelta(*args, **kwargs)

def since(time, *args, **kwargs):
    return get_time(time) + timedelta(*args, **kwargs)


def coerce_datetime_for_compare(a, b):
    if type(a)==type(b):
        return a,b
    if isinstance(a, (str, unicode)):
        a = str_to_date_or_time(a)
        return coerce_datetime_for_compare(a, b)
    elif isinstance(a, datetime) and isinstance(b, date):
        return a.date(), b
    elif isinstance(a, datetime) and isinstance(b, time):
        return a.time(), b
    else:
        b, a = coerce_datetime_for_compare(b, a)
        return a, b

def compare_datetime(a, b):
    a, b = coerce_datetime_for_compare(a,b)
    return cmp(a,b)

def parse_human_datetime(s):
    import parsedatetime.parsedatetime as pdt
    import logging
    pdt.log.setLevel(logging.INFO)

    cal = pdt.Calendar()
    s = s.replace('_', ' ')
    t, flag = cal.parse(s)
    if flag==0:
        return None
    else:
        return datetime(*t[:6])

def get_date_range_start(date):
    if not date or is_date_or_datetime(date):
        return date
    if not is_str(date):
        date = str(date)
    n = len(date)
    if n==4 and re.match(r'\d{4}', date):
        return '%s-01-01' % date
    elif n==7 and re.match(r'\d{4}-\d{2}', date):
        return '%s-01' % date
    else:
        t = parse_human_datetime(date)
        if t:
            return t
        else:
            return date

def get_datetime_range_start(t):
    return str_to_datetime(get_date_range_start(t))

def get_date_range_end(date):
    if not date or is_date_or_datetime(date):
        return date
    if not is_str(date):
        date = str(date)
    n = len(date)
    if n==4 and re.match(r'\d{4}', date):
        return '%s-12-31' % date
    elif n==7 and re.match(r'\d{4}-\d{2}', date):
        y = int(date[:4])
        m = int(date[5:7])
        d = calendar.monthrange(y,m)[1]
        return '%s-%02d' % (date, d)
    else:
        t = parse_human_datetime(date)
        if t:
            return t
        else:
            return date

# [start, end) style
def get_datetime_range_end(s):
    if not s or is_date_or_datetime(s):
        return s
    if not is_str(s):
        s = str(s)
    if len(s)<=len('2012-01-01'):
        t = str_to_datetime(get_date_range_end(s))
        t += timedelta(days=1)
    else:
        t = dateutil.parser.parse(s)
        if len(s)==len('2012-01-01 12'):
            t += timedelta(hours=1)
        elif len(s)==len('2012-01-01 12:00'):
            t += timedelta(minutes=1)
        elif len(s)==len('2012-01-01 12:00:00'):
            t += timedelta(seconds=1)
        else:
            raise Exception("invalide datetime str for get_date_range_end: %s" % s)
    return t

def split_datetime_range(date):
    if isinstance(date,(tuple,list)):
        d0,d1 = date
    elif isinstance(date, (str,unicode)) and date.find('~')>=0:
        d0,d1 = date.split('~')
    else:
        d0,d1 = date, date
    return d0, d1

def get_date_range(date):
    """
    >>> get_date_range('2010')
    ('2010-01-01', '2010-12-31')
    >>> get_date_range('2000-02')
    ('2000-02-01', '2000-02-29')
    >>> get_date_range('1900-02')
    ('1900-02-01', '1900-02-28')
    >>> get_date_range('2012-02')
    ('2012-02-01', '2012-02-29')
    >>> get_date_range((None,'2010'))
    (None, '2010-12-31')
    >>> get_date_range(['2010', None])
    ('2010-01-01', None)
    >>> get_date_range('2010-01-01')
    ('2010-01-01', '2010-01-01')
    """
    d0, d1 = split_datetime_range(date)
    return (get_date_range_start(d0), get_date_range_end(d1))

def get_datetime_range(date, **kwargs):
    if not kwargs:
        d0, d1 = split_datetime_range(date)
        return (get_datetime_range_start(d0), get_datetime_range_end(d1))
    else:
        start_time = kwargs.get('start_time')
        end_time = kwargs.get('end_time')
        delta = kwargs.get('delta')
        if start_time:
            start_time = get_datetime(start_time)
        if end_time:
            end_time = get_datetime(end_time)
        if delta:
            delta = get_timedelta(delta)
            if start_time:
                end_time = start_time + delta
            elif end_time:
                start_time = end_time - delta
            else:
                raise Exception("one of start_time, end_time is required")
        return (start_time, end_time)

def get_date_range_as_datetime(date):
    a = get_date_range(date)
    return map(str_to_datetime, a)

def date_sequence(start_date, change=1, end_date=None, max_day=None, to_str=None):
    raise Exception("use datetime_sequence instead")

def datetime_sequence(start_date, end_date=None, delta=None, count=None):
    if end_date is not None:
        end_date = get_datetime(end_date)
    start_date = get_datetime(start_date)

    if delta is None:
        if start_date < end_date:
            delta = timedelta(days=1)
        else:
            delta = timedelta(days= -1)
    else:
        delta = get_datedelta(delta)

    change = delta.total_seconds()

    d = start_date
    n = 0
    while True:
        n += 1
        if end_date is not None and (change>0 and d>end_date or change<0 and d<end_date):
            break
        if count is not None and n>count:
            break
        yield d
        d = d + delta

def get_timedelta(d):
    if isinstance(d, timedelta):
        return d
    elif isinstance(d, dict):
        return timedelta(**d)
    else:
        return timedelta(seconds=int(d))
    
def get_datedelta(self, d):
    if isinstance(d, timedelta):
        return d
    elif isinstance(d, dict):
        return timedelta(**d)
    else:
        return timedelta(days=int(d))
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()



