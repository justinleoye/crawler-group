import grequests
import redis

from redis_namespaced import NamespacedRedis

from pyutils import *

from quant_tsdb.lodb import LevelObjDB
from quant_rpc.mixins.event import EventMixin

from .plugins.file_cache import FileCachePlugin

from .crawler import Crawler
from .request import Request
from .response import Response
from .fetch import fetch

class CrawlerServer(EventMixin):
    def __init__(self, config):
        self.config = config

        file_path = config.get('cache_file_path', '/data/qfindb')
        db_path = config.get('cache_db_path', '/data/quant_crawler/cache')

        #TODO
        #self.cache_db = LevelObjDB(db_path, key='id')

        plugins = [
            FileCachePlugin(root=file_path, zip=True),
        ]

        c = config.get('redis', {})
        r = redis.StrictRedis(**c)
        self._redis = NamespacedRedis('quant_crawler:event', r)

        self._crawler = Crawler(plugins=plugins)

    def get_redis(self):
        return self._redis

    def crawl(self, request, options=None):
        if options is None:
            options = {}

        DEBUG("CrawlerServer.crawl: %s %s" % (request, options))

        socketio = request.get('socketio')
        streaming = request.get('streaming')

        if socketio:
            raise Exception("not support socketio")

        for req, rep in self._crawler.crawl(request, **options):
            DEBUG('%s %s' % (req, rep.__class__))
            if isinstance(rep, Response):
                if streaming:
                    return rep.lines
                else:
                    return rep.text
            else:
                return None


        """
        url = req.get('url')
        cache_id = req.get('cache_id')

        retry = req.get('retry')

        if cache_id is not None:
            c = self.cache.get(cache_id)
            if c is not None:
                rep = c.get('rep')
                if rep is not None:
                    rep = Response(response)
                    rep.set_encoding(req.encoding)
        else:
            rep = fetch(req)

        if rep is None:
            return None

        """
