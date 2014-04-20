import os
from time import sleep as time_sleep

try:
    from gevent import sleep as gevent_sleep
except:
    gevent_sleep = time_sleep

from .log_utils import *


if os.environ.get('SLEEP_DEBUG')=='1':
    SLEEP_DEBUG = WARN
else:
    SLEEP_DEBUG = DEBUG

def sync_sleep(s, msg=''):
    if s>0:
        SLEEP_DEBUG("[sync sleep] %s secs: %s" % (s, msg))
    time_sleep(s)

def async_sleep(s, msg=''):
    if s>0:
        SLEEP_DEBUG("[async sleep] %s secs: %s" % (s, msg))
    gevent_sleep(s)

sleep = async_sleep

