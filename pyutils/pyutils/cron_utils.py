from croniter import croniter

from pyutils.datetime_utils import to_datetime
from pyutils.type_utils import *

def get_cron_expr(conf):
    if conf is None:
        raise Exception("cron expr is None")

    elif is_str(conf):
        return conf

    elif is_list(conf):
        a = conf

    elif conf.get('expr'):
        return conf['expr']

    else:
        a = []
        #no year, croniter bug?
        for k in 'minute hour day_of_month month day_of_week second minute_of_day'.split():
            v = conf.get(k)
            if not v:
                if k=='second':
                    v = '0'
                else:
                    v = '*'
            a.append(v)

        if len(a)==7 and a[-1]=='*':
            a = a[:-1]

        if len(a)==6 and a[-1]=='*':
            a = a[:-1]

    return ' '.join(map(str,a))


def get_croniter(conf, start_time_key='start_time'):
    expr = get_cron_expr(conf)
    start_time = None
    t = conf.get(start_time_key)
    if t is not None:
        start_time = to_datetime(t)
    return croniter(expr, start_time)


