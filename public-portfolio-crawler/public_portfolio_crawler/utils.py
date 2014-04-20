from datetime import datetime
import re
import time

def public_symbol(s):
    return s[-6::]

def normalize_public_symbol(s):
    return s

def percent_normalize(n):
    try:
        f = float(n)*0.01
        return f
    except:
        return None

def date_normalize(date,f='%Y-%m-%d'):
    if date == '-' or date == '' or date == None:
        return None
    return datetime.strptime(date,f)

def num_normalize(s):
    try:
        d = int(s)
        return d
    except:
        return None

# if some percent has the error of '.' token by ',',replace the ',' to '.'
# the percent figure should has the symbol of '%' as end
def fix_percent_string_format(s):
    if isinstance(s,str):
        print 'has fix percent error:',s
        s = s.replace(',','.')
        s = s.replace('..','.')
        print 'fixed percent:',s
    return s

# if some float has the error of '.' token by ',',replace the ',' to '.'
def fix_float_string_format(s):
    print 's in fix_float_string_format:',repr(s)
    if isinstance(s,str) or isinstance(s,unicode):
        print 'has fix float error:',s
        # whether the s is a '23,232,000' like number
        if not re.search(r',\d{3},?',s):
            s = s.replace(',','.')
            s = s.replace('..','.')
            s = s.replace('O','0')
            s = s.replace('o','0')
            s = s.replace(' ','')
        else:
            s = s.replace(',','')
        print 'fixed float:',s
    return s

def float_normalize(s):
    try:
        print 's in float_normalize:',s
        f = float(s)
        print 's in float_normalize after floated:',f
        return f
    except (ValueError,TypeError),e:
        print e
        return None

def str_normalize(s):
    try:
        if isinstance(s,unicode):
            s = s.encode('utf8')
        if not isinstance(s,str):
            s = str(s)
        # the following conditions all depend
        if s.startswith('--') or s == '':
            s = None
        if isinstance(s, str):
            s = s.decode('utf8')
        return s
    except TypeError:
        return None

def value_normalize(n=0,m='w'):
    if isinstance(n, int) or isinstance(n, float):
        if m == 'q':
            return n*1000.0
        if m == 'w':
            return n*10000.0
        elif m == 'y':
            return n*100000000.0
    else:
        return float(0)

def volume_normalize(n):
    if isinstance(n, int) or isinstance(n, float):
        return int(n*10000)
    else:
        return 0


def get_timestring_service(start_date=None,reverse=True):
    time_list = []
    s_list = []
    n_list = []
    # now
    now = datetime.now()
    y = now.strftime('%Y')
    m = now.strftime('%m')
    d = now.strftime('%d')

    if int(m) == 12 and int(d) == 31:
        n_list.append('12-31')
    if int(m) >9 or (int(m) == 9 and int(d) == 30):
        n_list.append('09-30')
    if int(m) >6 or (int(m) == 6 and int(d) == 30):
        n_list.append('06-30')
    if int(m) > 3 or (int(m) == 3 and int(d) == 31):
        n_list.append('03-31')

    # start time
    if start_date and isinstance(start_date,str):
        start = datetime.strptime(start_date,'%Y-%m-%d')
        s_y = start.strftime('%Y')
        s_m = start.strftime('%m')
        s_d = start.strftime('%d')
        if int(s_m) <= 12:
            s_list.append('12-31')
        if int(s_m) <= 9:
            s_list.append('09-30')
        if int(s_m) <= 6:
            s_list.append('06-30')
        if int(s_m) <= 3:
            s_list.append('03-31')
    else:
        s_y = y

    if reverse:
        time_list += [n_y + '-' + m_d for m_d in n_list]
        for year in range(int(y)-1,int(s_y),-1):
            time_list += [str(year)+'-'+m_d for m_d in ['12-31','09-30','06-30','03-31']]
        time_list += [s_y +'-'+ m_d for m_d in s_list]
    else:
        time_list += [s_y +'-'+ m_d for m_d in s_list[::-1]]
        for year in range(int(s_y)+1, int(y)):
            time_list += [str(year)+'-'+m_d for m_d in ['03-31','06-30','09-30','12-31']]
        time_list += [n_y +'-'+ m_d for m_d in n_list[::-1]]
    #print time_list
    for timestring in time_list:
        yield timestring
