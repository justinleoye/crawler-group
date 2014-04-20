from pyutils import *
from pyutils.path_utils import *
from pyutils.file_utils import *

from ..plugin import CrawlerPlugin
from ..exception import IgnoreRequest, IgnoreException

class FileErrorCheckPlugin(CrawlerPlugin):
    def __init__(self, error_response_contains=None, error_response=None, auto_skip_error=True):
        self.error_response = self.to_unicode(error_response, 'utf8')
        self.error_response_contains = self.to_unicode(error_response_contains, 'utf8')
        self.auto_skip_error = auto_skip_error

    def to_unicode(self, s, encoding=None):
        if s is None:
            return None

        if encoding and not isinstance(s, unicode):
            s = s.decode(encoding)
        return s

    def get_target(self, request):
        target = request.get('full_target')
        if target is None:
            return None
            #raise Exception('FileErrorCheckPlugin need full_target field in request')
        return target

    def get_error_target(self, request):
        t = self.get_target(request)
        if t is None:
            return None
        else:
            return t+ '.__ERROR__'

    def process_request(self, request, crawler):
        error_target = self.get_error_target(request)
        if error_target is None:
            return
        if self.auto_skip_error and file_exists(error_target, minsize=0):
            raise IgnoreRequest("skip as auto_skip_error set and __ERROR__ file already exists")

    def process_response(self, request, response, crawler):
        error_target = self.get_error_target(request)
        if error_target is None:
            return

        r = response.text #unicode

        er = self.error_response
        erc = self.error_response_contains
        if not isinstance(r, unicode):
            if er is not None:
                er = er.encode('utf8')
            if erc is not None:
                erc = erc.encode('utf8')

        if er is not None and r==er.strip():
            open_file_force(error_target, 'w').close()
            raise Exception("downloading error because of response is: %s" %\
                self.error_response)

        if erc is not None and r.find(erc)>=0:
            open_file_force(error_target, 'w').close()
            raise Exception("downloading error because of response contains: %s" %\
                self.error_response_contains)

        if os.path.exists(error_target):
            os.remove(error_target)

    def process_exception(self, request, exception, crawler):
        pass



