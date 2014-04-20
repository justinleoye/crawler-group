import types
import collections

def is_list(x):
    return isinstance(x, (list,tuple))

def is_seq(x):
    return isinstance(x, collections.Sequence)

def is_str(x):
    return isinstance(x, (str,unicode))

def is_dict(x):
    return isinstance(x, collections.Mapping)

def is_generator(x):
    return type(x) is types.GeneratorType

def get_list(x):
    if x is None:
        return []
    elif isinstance(x, list):
        return x
    elif isinstance(x, tuple):
        return list(x)
    elif is_generator(x):
        return list(x)
    else:
        return [x]

def get_dict(keys, values):
    return dict(zip(keys, get_list(values)))

def auto_convert(x):
    try:
        return int(x)
    except:
        try:
            return float(x)
        except:
            try:
                return str(x)
            except:
                return x
