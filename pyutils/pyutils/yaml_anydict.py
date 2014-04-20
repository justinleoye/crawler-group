#http://pyyaml.org/ticket/29

#yaml_anydict.py
import yaml
from yaml.representer import Representer
from yaml.constructor import Constructor, MappingNode, ConstructorError

from .log_utils import *

def dump_anydict_as_map( anydict):
    yaml.add_representer( anydict, _represent_dictorder)
def _represent_dictorder( self, data):
    return self.represent_mapping('tag:yaml.org,2002:map', data.items() )

class Loader_map_as_anydict( object):
    'inherit + Loader'
    anydict = None      #override
    @classmethod        #and call this
    def load_map_as_anydict( klas):
        yaml.add_constructor( 'tag:yaml.org,2002:map', klas.construct_yaml_map)

    'copied from constructor.BaseConstructor, replacing {} with self.anydict()'
    def construct_mapping(self, node, deep=False):
        if not isinstance(node, MappingNode):
            raise ConstructorError(None, None,
                    "expected a mapping node, but found %s" % node.id,
                    node.start_mark)
        mapping = self.anydict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as exc:
                raise ConstructorError("while constructing a mapping", node.start_mark,
                        "found unacceptable key (%s)" % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

    def construct_yaml_map( self, node):
        data = self.anydict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

class TupleDict(dict):
    def __init__(self, *args, **kwargs):
        if len(args)==1 and isinstance(args[0], list):
            super(TupleDict, self).__init__(*args, **kwargs)
            self.values = list(args[0])
        else:
            super(TupleDict, self).__init__(*args, **kwargs)
            self.values = self.items()

    def __setitem__(self, key, value):
        super(TupleDict, self).__setitem__(key, value)
        self.values.append((key,value))

    def update(self, other):
        super(TupleDict, self).update(other)
        if isinstance(other, TupleDict):
            self.values += other.values
        else:
            self.values += other.items()

    def tuples(self):
        return self.values

    def __str__(self):
        return str(self.values)

    def to_dict(self):
        r = {}
        for k,v in self.values:
            if isinstance(v, TupleDict):
                v = v.to_dict()
            elif isinstance(v, list):
                a = []
                for x in v:
                    if isinstance(x, TupleDict):
                        x = x.to_dict()
                    a.append(x)
                v = a
            r[k] = v
        return r

class TupleDictLoader(Loader_map_as_anydict, yaml.Loader):
   anydict = TupleDict

import collections
class OrderedDictLoader(Loader_map_as_anydict, yaml.Loader):
   anydict = collections.OrderedDict

def load(s, type='TupleDict'):
    if type=='TupleDict':
        Loader = TupleDictLoader
    else:
        Loader = OrderedDictLoader
    Loader.load_map_as_anydict()
    return yaml.load(s, Loader=Loader)

def dump(o, type='TupleDict'):
    if type=='TupleDict':
        Dict = TupleDict
        Loader = TupleDictLoader
    else:
        Dict = OrderedDict
        Loader = OrderedDictLoader
    yaml_anydict.dump_anydict_as_map(Dict)
    return yaml.dump(o)


