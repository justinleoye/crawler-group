"""
ref:
http://doc.scrapy.org/en/0.16/topics/downloader-middleware.html
"""

class CrawlerPlugin(object):
    def set_crawler(self, crawler):
        self.crawler = crawler

    #TODO use self.crawler in all methods
    def process_request(self, request, crawler):
        pass

    def process_response(self, request, response, crawler):
        pass

    def process_exception(self, request, exception, crawler):
        pass

    def process_done(self, request, crawler):
        pass

