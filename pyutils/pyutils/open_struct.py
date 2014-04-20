#http://www.dzone.com/snippets/python-openstruct

from pyutils import *
from collections import MutableMapping

__all__ = ['OpenStruct']

class OpenStruct(dict):
    def __setattr__(self,key,value):
        self[key] = value
        return value

    def __getattr__(self, key):
        if key in self:
            return self[key]
        else:
            raise AttributeError()
        """
        #NOTE: cause error in yaml dump
        return self.get(key)
        """

class DefaultOpenStruct(dict):
    def __setattr__(self,key,value):
        self[key] = value
        return value

    def __getattr__(self, key):
        if not key.startswith('_'):
            #NOTE: cause error in yaml dump
            return self.get(key)
        elif key in self:
            return self[key]
        else:
            raise AttributeError()

class OpenStruct2(MutableMapping):
    def __init__(self, *args, **dic):
        for d in args:
            self.__dict__.update(d)
        self.__dict__.update(dic)

    """
    #get/set attribute
    def __getattr__(self, key):
        return None
    """

    def __setattr__(self,key,value):
        self.__dict__[key] = value
        return value
        
    # MutableMapping
    def __getitem__(self, key):
        return self.__dict__.get(key)

    def __setitem__(self, key, value):
        self.__dict__[key] = value
        return value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    # dict
    def get(self, key, default=None):
        return self.__dict__.get(key, default)
        
    # Container
    def __contains__(self, key):
        return key in self.__dict__

    # other
    def __eq__(self, other):
        if not hasattr(other, '__dict__'):
            return False
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.__dict__)

