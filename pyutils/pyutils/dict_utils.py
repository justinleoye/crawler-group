def del_kwargs(kwargs, key, default=None):
    v = None
    if key in kwargs:
        v = kwargs[key]
        del kwargs[key]
    if v is None:
        v = default
    return v
    
def reverse_update(d1, d2):
    for k,v in d2.iteritems():
        if not k in d1:
            d1[k] = v
    return d1

def extend(base, ext):
    for k,v in ext.iteritems():
        base[k] = v
    return base

def def_kwargs(kwargs, **defaults):
    return reverse_update(kwargs, defaults)

set_dict_defaults = def_kwargs

def sub_dict(d, keys):
    if not d:
        return d
    return dict((k,d[k]) for k in keys if k in d)

def recursive_merge(base, ext):
    for k,v in ext.items():
        if isinstance(v, dict):
            if not k in base or not isinstance(base[k], dict):
                base[k] = v
            else:
                recursive_merge(base[k], v)
        else:
            base[k] = v
    return base

recursive_extend = recursive_merge

def cleanup_dict(d, value=None):
    for k in d.keys():
        if d[k]==value:
            del d[k]
    return d

            

