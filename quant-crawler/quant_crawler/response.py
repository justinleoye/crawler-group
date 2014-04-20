import requests.models

from pyutils import *
from pyutils.unicode_utils import str_to_unicode

class Response(dict):
    def unicode_text(self, encoding='utf8'):
        if encoding is None:
            return self.content
        return str_to_unicode(self.content, encoding)

    def set_encoding(self, encoding):
        self['text'] = self.unicode_text(encoding)

    def set_content(self, content):
        if not self.resp:
            self['__resp__'] = requests.models.Response()
        self.resp._content = content
        self.resp._content_consumed = True

    @property
    def headers(self):
        h = self.get('headers')
        if h is None:
            r = self.resp
            if r is not None:
                h = r.headers
        return h

    @property
    def cached(self):
        return self.get('__cached__') == True

    @cached.setter
    def cached(self, value):
        self['__cached__'] = value

    @property
    def chunk_size(self):
        return self.get('chunk_size') or 512

    @property
    def resp(self):
        return self.get('__resp__')

    @property
    def socketio(self):
        return self.get('__socketio__')

    @property
    def streaming(self):
        return bool(self.get('streaming'))

    @property
    def binary(self):
        return bool(self.get('binary'))

    @property
    def text(self):
        #Content of the response, in unicode (if possible)
        if 'text' in self:
            return self['text']
        elif self.resp:
            return self.resp.text
        else:
            ERROR(self)
            return None

    @property
    def text_lines(self):
        return self.text.split('\n')

    @property
    def lines(self):
        if self.get('_line_stream'):
            for x in self['_line_stream']:
                yield x
        else:
            for line in self.resp.iter_lines(self.chunk_size):
                yield line + '\n'

    
    @property
    def content(self):
        #Content of the response, in bytes
        if self.resp is None:
            return self.text
        else:
            return self.resp.content

    @classmethod
    def from_result(cls, r):
        if isinstance(r, types.GeneratorType):
            return cls({
                '_line_stream': r,
                'streaming': True
            })
        else:
            return cls({
                'text': r
            })

    def done(self):
        if isinstance(self.resp, requests.models.Response):
            if self.resp.raw is not None:
                DEBUG_("close resp")
                self.resp.close()


        
