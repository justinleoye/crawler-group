from .backend import Backend

class YamlBackend(Backend):
    def __init__(self, *args, **kwargs):
        super(YamlBackend, self).__init__(*args, **kwargs)
        self.config = load_config(self.endpoint, as_dict=True)

    def _get(self, key):
        raise Exception("TO TEST")

        keys = self.get_key(key)
        r = self.config
        for k in keys:
            if isinstance(r, dict):
                if not k in r:
                    raise KeyError
                else:
                    r = r[k]
            elif isinstance(r, list):
                k = int(k)
                if k<0 or k>len(r):
                    raise KeyError
                r = r[k]
            else:
                raise KeyError
        return r

    def _set(self, key, value, ttl=None):
        """
        a.b.c = 1
        r['a']['b']['c'] = 1
        """
        keys = key.split(self.key_sep)
        r = self.config
        for k in keys[:-1]:
            if isinstance(r, dict):
                if not k in r:
                    r[k] = {}
                r = r[k]
            else:
                raise Exception("invalid key: %s" % key)
        r[keys[-1]] = value


