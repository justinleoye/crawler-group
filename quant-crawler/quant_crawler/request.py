
class Request(dict):
    @property
    def encoding(self):
        return self.get('encoding')

    @property
    def url(self):
        return self.get('url')

