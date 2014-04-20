from .type_utils import *

def str_abbr(s, maxlen=128):
    if len(s)>maxlen:
        n = maxlen/2
        return s[:n] + s[-n:]
    else:
        return s

def to_unicode(s, coding='utf8'):
    if isinstance(s, str):
        s = s.decode(coding)
    elif not isinstance(s, unicode):
        s = unicode(s)
    return s


def recursive_substitute(obj, params, f=None):
    if is_str(obj):
        if f is None:
            return obj % params
        else:
            return f(obj, params)

    elif is_list(obj):
        return [recursive_substitute(x, params, f) for x in obj]

    elif is_dict(obj):
        r = {}
        for k,v in obj.iteritems():
            k = recursive_substitute(k, params, f)
            r[k] = recursive_substitute(v, params, f)
        return r

    else:
        return obj

#https://pypi.python.org/pypi/inflect
def pluralize(s, special=None):
    if special is not None and s in special:
        return special[s]
    if not s.endswith('s'):
        return s + 's'
    else:
        return s

def singularize(s, special=None):
    if special is not None and s in special:
        return special[s]
    if s.endswith('s'):
        return s[:-1]
    else:
        return s

