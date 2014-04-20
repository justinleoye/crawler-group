import gevent

from pyutils import *
from ..plugin import CrawlerPlugin
from ..exception import IgnoreRequest, IgnoreException

DEFAULT_USRE_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31'

class ValidatePlugin(CrawlerPlugin):
    def __init__(self):
        pass

    def process_request(self, request, crawler):
        url = request.get('url')
        socketio = request.get('socketio')
        if url is None and not socketio:
            raise Exception("url and socketio missing")

        if request.get('headers') is None:
            request['headers'] = {}

        headers = request['headers']

        user_agent = request.get('user_agent')
        if user_agent is None:
            user_agent = DEFAULT_USRE_AGENT
        headers['User-Agent'] = user_agent

        referer = request.get('referer')
        if referer is None:
            referer = url
        headers['Referer'] = referer


    def process_response(self, request, response, crawler):
        pass




