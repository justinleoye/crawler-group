
from pyutils import *
from pyutils.serializers import json_ext
from pyutils.create_obj import create_obj_from_config

from quant_serviced import serviced

from quant_executor import Executor

class CrawlerExecutor(Executor):
    def tsdb(self):
        return serviced.get_service_client('quant_tsdb')
        
    def execute(self, job):
        debug = job.get('debug')

        if job.get('debug'):
            crawler_server = None
        else:
            crawler_server = serviced.get_service_client('quant_crawler')
        kwargs = {
            'crawler_server': crawler_server
        }
        self.crawler = create_obj_from_config(job['crawler'], kwargs=kwargs)
        stream = self.crawler.feed(job)

        output = job.get('output')
        if debug or output is None:
            #start generator
            for x in stream:
                print json_ext.dumps(x)
            return None
        else:
            tsdb = self.tsdb()
            tsdb.create_series(output)
            tsdb.write_series(output, None, stream, timeout=None)

    def pause(self):
        super(CrawlerExecutor, self).pause()
        return self.crawler.pause()

    def cont(self):
        super(CrawlerExecutor, self).cont()
        return self.crawler.cont()


