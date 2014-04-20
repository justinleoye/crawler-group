#coding:utf-8

import json

f = open('hedge_funds_Warren_Buffet.json','r')
data_json = json.loads(f.read())
f.close()


pre_time_dict = {
    '03-31': ['12-31',True],
    '06-30': ['03-31',False],
    '09-30': ['06-30',False],
    '12-31': ['09-30',False]
}
next_time_dict = {
    '03-31': ['06-30', False],
    '06-30': ['09-30', False],
    '09-30': ['12-31', False],
    '12-31': ['03-31', True]
}

time_transfer = {
     '03-31': 'Q1',
     '06-30': 'Q2',
     '09-30': 'Q3',
     '12-31': 'Q4',
     'Q1': 'Q1',
     'Q2': 'Q2',
     'Q3': 'Q3',
     'Q4': 'Q4',
}

def get_previous_time(t):
    year,month_day = t.split('-',1)
    pre_month_day = pre_time_dict[month_day][0]
    if pre_time_dict[month_day][1]:
        year = str(int(year)-1)
    pre_t = year + '-' + pre_month_day
    return pre_t

def get_next_time(t):
    year,month_day = t.split('-',1)
    next_month_day = next_time_dict[month_day][0]
    if next_time_dict[month_day][1]:
        year = str(int(year)-1)
    next_t = year + '-' + next_month_day
    return next_t

data = []
for key,item in data_json.iteritems():
    print 'key:',key
    pre_t = get_previous_time(key)
    print 'pre:',pre_t
    next_t = get_next_time(key)
    for k,v in data_json[key].iteritems():
        if data_json.has_key(pre_t):
            if data_json[pre_t].has_key(k):
                print key
                print pre_t
                print data_json[key][k]['hold_volume'],'-',data_json[pre_t][k]['hold_volume']
                v['change_volume'] = data_json[key][k]['hold_volume']-data_json[pre_t][k]['hold_volume']
                print v['change_volume']
                if v['change_volume'] > 0:
                    v['activity'] = 'Increase'
                elif v['change_volume'] == 0:
                    v['activity'] = None
                else:
                    v['activity'] = 'Decrease'
                if v['hold_volume'] <= 0:
                    v['activity'] = 'Soldout'

            else:
                v['change_volume'] = v['hold_volume']
                v['activity'] = 'New'

            y,q = v['time'].split('-',1)
            q = time_transfer[q]
            v['time'] = y + '-' + q

data_list = sorted(data_json.iteritems(),key=lambda d:d[0],reverse=True)
for item in data_list:
    for k,change in item[1].iteritems():
        if change['activity'] not in ['Increase','Decrease','Soldout','New']:
            continue
        data.append(change)
f = open('hedge_Warren.json', 'w')
f.write(json.dumps(data))
f.close()

