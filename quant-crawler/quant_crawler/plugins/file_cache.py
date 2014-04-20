import gevent
import os

from pyutils import *
from pyutils import sleep_utils
from pyutils.path_utils import *
from pyutils.file_utils import *
from pyutils.zipfile_utils import *

from ..plugin import CrawlerPlugin
from ..response import Response
from ..exception import IgnoreRequest, IgnoreException

class FileCachePlugin(CrawlerPlugin):
    def __init__(self, root=None, zip=False, target_suffix=None, auto_skip=True, sleep_if_no_cache=None, sleep_first_time=True):
        self.root = None
        if root:
            self.root = os.path.expanduser(root)

        self.zip = zip
        self.auto_skip = auto_skip
        self.target_suffix = target_suffix
        self.sleep_if_no_cache = sleep_if_no_cache

        self._first = True
        self.sleep_first_time = sleep_first_time

    def get_download_target(self, url, target=None):
        #skip cache if target is None
        #if target is None:
        #    target = url.split('/')[-1]
        return target

    def process_request(self, request, crawler):
        target = request.get('target')
        url = request.get('url')

        target = self.get_download_target(url, target)
        if target is None:
            return

        if self.root:
            target = os.path.join(self.root, target)

        if self.target_suffix is not None:
            target += self.target_suffix

        target = normalize_zip_filename(target, self.zip)
        request['full_target'] = target

        if self.auto_skip and file_exists(target, minsize=1):
            INFO("skip as target already exists: %s" % target)
            r = Response({'headers': {}})

            if not request.get('raw_file'):
                content = read_from_file(target)
                r.set_content(content)
                r.set_encoding(request.encoding)

            r.cached = True
            return r

    def process_response(self, request, response, crawler):
        if request.get('raw_file'):
            response['raw_file'] = True
            response['raw_file_name'] = request['full_target']

        if not response.cached and request.get('full_target'):
            #write_to_file ensure path exists
            #write raw content to file
            write_to_file(response.content, request['full_target'], zip=self.zip)
            s = self.sleep_if_no_cache

            #don't sleep for first response
            if s is not None and (self.sleep_first_time or not self._first):
                sleep_utils.sleep(s, 'FileCachePlugin: no_cache')
            self._first = False


