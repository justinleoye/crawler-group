from .type_utils import *

def remove_value(a, value):
    if is_list(a):
        b = []
        for x in a:
            if x != value:
                b.append(x)
        return b
    elif isinstance(a, dict):
        b = {}
        for k,v in a.iteritems():
            if v != value:
                b[k] = v
        return b

def remove_value_iter(a, value):
    for v in a:
        if v != value:
            yield v

def compact_collection(a, removed_value=None):
    if is_generator(a):
        return remove_value_iter(a, remove_value)
    else:
        return remove_value(removed_value)
    
