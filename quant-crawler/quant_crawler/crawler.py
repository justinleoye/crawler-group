import gevent
import random
import operator
import time
import yaml
import objgraph
import gc
from collections import defaultdict

import updater

from pyutils import *
from pyutils import sleep_utils
from pyutils.create_obj import *
from pyutils.gc_utils import *
from pyutils.pause_utils import Pausable

from .request import Request
from .response import Response
from .plugins import *
from .exception import *
from .plugin import CrawlerPlugin

__all__ = ['Crawler', 'Response', 'Request']

class Crawler(updater.Updater, Pausable):
    def __init__(self, plugins=None, pipelines=None, crawler_server=None, skip_done=None, **kwargs):
        Pausable.__init__(self)
        self.crawled = []
        self.crawled_items = []
        self.plugins = []
        self.pipeline = None
        self.crawler_server = crawler_server
        self.skip_done = skip_done
        self.reqs = []

        if pipelines:
            a = []
            for conf in pipelines:
                p = create_obj_with_import(conf, default_env=globals())
                a.append(p)
            self.pipeline = updater.utils.updater_pipeline(a)

        before_plugins = [
            ValidatePlugin()
        ]

        after_plugins = [
            DefaultPlugin(self.crawler_server),
            #NOTE: add self as a plugin
            self
        ]

        middle_plugins = []
        if plugins:
            for conf in plugins:
                if isinstance(conf, CrawlerPlugin):
                    p = conf
                else:
                    p = create_obj_with_import(conf, default_env=globals())
                middle_plugins.append(p)
                
        for p in before_plugins:
            p.set_crawler(self)
            self.plugins.append(p)
        
        for p in middle_plugins:
            p.set_crawler(self)
            self.plugins.append(p)

        for p in after_plugins:
            p.set_crawler(self)
            self.plugins.append(p)

    #Crawler Plugin interface
    def set_crawler(self, crawler):
        self.crawler = crawler

    def process_request(self, request, crawler):
        pass

    def process_done(self, request, crawler):
        pass

    def process_response(self, request, response, crawler):
        pass

    def process_exception(self, request, exception, crawler):
        pass

    def handle_request(self, request):
        self.reqs.append(request)
        for p in self.plugins:
            DEBUG_("process_request:%s" % p.__class__.__name__)
            r = p.process_request(request, self)

            if isinstance(r, Response):
                self.handle_response(request, r)
                break

    def handle_done(self, request):
        DEBUG("handle_done for %s" % request.url)
        for p in self.plugins:
            p.process_done(request, self)

    def to_generator(self, r):
        if is_generator(r):
            for x in r:
                yield x
        else:
            yield r

    def handle_response(self, request, response):
        self.crawled.append([request, response])
        items = []
        for p in self.plugins:
            DEBUG_("process_response:%s" % p.__class__.__name__)
            ret = p.process_response(request, response, self)
            for r in self.to_generator(ret):
                if isinstance(r, Response):
                    self.handle_response(request, r)
                    #don't break

                elif isinstance(r, Request):
                    self.handle_request(r)
                    #don't break

                elif isinstance(r, dict):
                    items.append(r)

        if items:
            self.crawled_items.append([request, items])

    def handle_exception(self, request, exception):
        for p in self.plugins:
            DEBUG("process_exception:%s" % p.__class__.__name__)
            r = p.process_exception(request, exception, self)

            if isinstance(r, Response):
                DEBUG("process_exception as response:%s" % response)
                self.handle_response(request, r)
                break

            elif isinstance(r, Request):
                DEBUG("process_exception as request:%s" % request)
                self.handle_request(request)
                break

    def crawl(self, request, **kwargs):
        DEBUG("[crawler] crawl request: %s" % yaml.dump(request))
        self.crawled = []
        self.crawled_items = []

        if not isinstance(request, Request):
            request = Request(request)

        try:
            self.handle_request(request)
            for x in self.crawled:
                yield x

            for x in self.crawled_items:
                yield x
        except IgnoreRequest, e:
            return

        except Exception, e:
            ERROR(TRACE_BACK(e))
            ERROR(e)
            self.handle_exception(request, e)
            return

        '''
        req = urllib2.Request(url)
        for k,v in headers.items():
            req.add_header(k, v)
        resp = urllib2.urlopen(req)
        stream = iter(resp)
        '''

        '''
        h = httplib2.Http(".cache")
        resp, content = h.request(url, headers=headers)
        stream = iter(content)

        '''

    def pipelined_stream(self, stream):
        if not self.pipeline:
            return stream
        else:
            return self.pipeline.feed_all(stream)

    def response_stream(self, job):
        failed = 0
        max_fail = job.get('max_fail')

        show_memory_stats = job.get('show_memory_stats')

        if show_memory_stats:
            last_stat = defaultdict(int)
            #gc.set_debug(gc.DEBUG_LEAK)
            #gc.set_debug(gc.DEBUG_SAVEALL)
            gc.set_debug(gc.DEBUG_UNCOLLECTABLE)

        for request in self.generate_tasks(job):
            self.wait_if_paused()
            gc.collect()
            if show_memory_stats:
                stat = type_stats_size()
                diff = diff_stats(last_stat, stat)

                DEBUG("memory stats:")
                DEBUG("DIFF:")
                for x in sorted_stats(diff)[:20]:
                    DEBUG('    %s:%s' % (x[0], x[1]))
                DEBUG("ALL:")
                for x in sorted_stats(stat)[:100]:
                    DEBUG('    %s:%s' % (x[0], x[1]))
                last_stat = stat

                if gc.garbage:
                    DEBUG("GARBAGE COUNT")
                    s = type_stats_count(gc.garbage)
                    for x in sorted_stats(s)[:20]:
                        DEBUG('    %s:%s' % (x[0], x[1]))

                    DEBUG("GARBAGE SIZE")
                    s = type_stats_size(gc.garbage)
                    for x in sorted_stats(s)[:20]:
                        DEBUG('    %s:%s' % (x[0], x[1]))

                    ##TODO
                    lx = []
                    for x in gc.garbage:
                        if isinstance(x, list):
                            if len(x)>0:
                                lx.append(x)
                                #print '====', len(x)
                                if len(x)>200:
                                    x = x[:100] + x[-100]
                                s = ' '.join(str_abbr(z, 32) for z in x)
                                #print '----', s
                            """
                            if random.randint(0, 10000)==0:
                                show_backrefs([x])
                                break
                            """
                    show_backrefs(lx)
                #show_backrefs_by_type('Kline')
            try:
                for x in self.crawl(request):
                    if x is not None:
                        DEBUG_(x)
                        yield x
                        #important!! 
                        #blocked in publisher subscribe if not sleep
                        sleep_utils.async_sleep(0)
                self.task_done(job, request)
            except Exception, e:
                tb = TRACE_BACK()
                failed += 1
                ERROR("Crawler exception: %s\n%s" % (str(e), tb))
                if max_fail is None or failed>max_fail:
                    raise e

    def filtered_stream(self, job):
        if job.get('chain_subtask_result')==True:
            for x in self.response_stream(job):
                request, response = x
                if not isinstance(response, Response) and isinstance(response, list):
                    #is a crawled item
                    for item in response:
                        yield item
                else:
                    try:
                        for y in self.filter(request, response):
                            yield y
                    finally:
                        response.done()
        else:
            for x in self.response_stream(job):
                request, response = x
                if not isinstance(response, Response) and isinstance(response, list):
                    #is a crawled item
                    items = response
                    yield items, None
                else:
                    yield self.filter(request, response), response

    def feed(self, job):
        #SET_TRACE()
        DEBUG_("crawling job %s" % yaml.dump(job))
        if job.get('chain_subtask_result')==True:
            for x in self.pipelined_stream(self.filtered_stream(job)):
                yield x
        else:
            for stream, resp in self.filtered_stream(job):
                for x in self.pipelined_stream(stream):
                    yield x
                if isinstance(resp, Response):
                    resp.done()

    def feed_done(self):
        for r in self.reqs:
            self.handle_done(r)
        self.reqs = []
        return []

    def task_event(self, job, t):
        em = self.crawler_server
        ce = job.get('crawler_event')
        if em is None or ce is None:
            return None
        id = t.get('task_id')
        if id is None:
            return None
        e = 'crawler:done:%s:%s' % (ce.get('name'), id)
        expire = ce.get('expire')
        return e, expire

    def task_done(self, job, t):
        e = self.task_event(job, t)
        if e is not None:
            self.crawler_server.fire_event(e[0], e[1])

    def check_task_done(self, job, t):
        e = self.task_event(job, t)
        if e is not None:
            return self.crawler_server.check_event(e[0])
        else:
            return False

    def generate_tasks(self, job):
        for t in self.tasks(job):
            if not self.check_task_done(job, t):
                yield t
            else:
                DEBUG("skip crawler task, already done: %s" % t['task_id'])

    def filter(self, request, response):
        yield response.content

    def tasks(self, job):
        yield job

