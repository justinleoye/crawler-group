from types import MethodType

class JsObject(dict):
    def __init__(self, *args, **kwargs):
        super(JsObject, self).__init__(*args, **kwargs)
        self.__dict__ = self 


#http://www.ianlewis.org/en/dynamically-adding-method-classes-or-class-instanc

def add_method_to_instance(obj, meth, name=None):
    if name is None:
        name = meth.__name__
    x = MethodType(meth, obj, obj.__class__)
    setattr(obj, name, x)
    return x

def add_method_to_class(cls, meth, name=None):
    if name is None:
        name = meth.__name__
    x = MethodType(meth, None, cls)
    setattr(cls, name, x)
    return x

