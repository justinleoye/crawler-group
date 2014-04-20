import copy_reg
import types

def _reduce_method(m):
    return (getattr, (m.__self__, m.__func__.__name__))
copy_reg.pickle(types.MethodType, _reduce_method)


#json json_dict yaml pickle
_pickle_type = 'pickle'

def pickle_dumpload(obj, pickle_type=None):
    return pickle_loads(pickle_dumps(obj, pickle_type), pickle_type)

def pickle_loaddump(s, pickle_type=None):
    return pickle_dumps(pickle_loads(s, pickle_type), pickle_type)

def assert_pickle_dumpload(obj, pickle_type=None):
    assert pickle_dumpload(obj, pickle_type=pickle_type)==obj

def assert_pickle_loaddump(s, pickle_type=None):
    assert pickle_loaddump(s, pickle_type=pickle_type)==s

def pickle_dumps(obj, pickle_type=None):
    if pickle_type is None:
        pickle_type = _pickle_type

    if pickle_type=='json_dict':
        import jsonpickle.pickler
        j = jsonpickle.pickler.Pickler(unpicklable=True, max_depth=None)
        return j.flatten(obj)
    elif pickle_type=='json':
        import jsonpickle
        return jsonpickle.encode(obj)
    elif pickle_type=='yaml':
        import yaml
        return yaml.dump(obj)
    elif pickle_type=='pickle_hp':
        import pickle
        return pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)
    elif pickle_type=='pickle':
        import pickle
        return pickle.dumps(obj)
    elif pickle_type=='cpickle':
        import cPickle
        return cPickle.dumps(obj)
    else:
        raise Exception("unkown pickle type")

def pickle_loads(s, pickle_type=None):
    if pickle_type is None:
        pickle_type = _pickle_type

    if pickle_type=='json_dict':
        import jsonpickle.unpickler
        j = jsonpickle.unpickler.Unpickler()
        return j.restore(s)
    elif pickle_type=='json':
        import jsonpickle
        return jsonpickle.decode(s)
    elif pickle_type=='yaml':
        import yaml
        return yaml.load(s)
    elif pickle_type=='pickle_hp':
        import pickle
        return pickle.loads(s, pickle.HIGHEST_PROTOCOL)
    elif pickle_type=='pickle':
        import pickle
        return pickle.loads(s)
    elif pickle_type=='cPickle':
        import cPickle
        return cPickle.loads(s)
    else:
        raise Exception("unkown pickle type")


class SerializableMixin(object):
    def pickle(self, obj):
        return pickle_dumps(obj, self.pickle_type)

    def unpickle(self, obj):
        return pickle_loads(obj, self.pickle_type)


