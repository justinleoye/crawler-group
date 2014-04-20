import time
import gevent

from pyutils import *
from pyutils import sleep_utils
from quant_utils.time_interval import TimeIntervalList

from .crawler import Crawler

class ContinuousCrawler(Crawler):
    def generate_tasks(self, job):
        sleep = job.get('sleep', 5)
        wait_sleep = job.get('wait_sleep', 5)

        interval = TimeIntervalList(intervals=job.get('intervals'), none_is_all=True)
        while True:
            now = time.time()
            if interval.before_start(now):
                DEBUG("sleep before start")
                sleep_utils.sleep(check_sleep)
            elif interval.after_end(now):
                DEBUG("break after end")
                break
            else:
                if interval.include(now):
                    for t in self.tasks(job):
                        yield t
                    DEBUG("sleep inside working interval")
                    sleep_utils.sleep(sleep)
                else:
                    DEBUG("sleep outside working interval")
                    sleep_utils.sleep(wait_sleep)
            
