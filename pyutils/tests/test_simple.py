from pyutils import *
from pyutils.open_struct import *

def test_simple():
    assert get_list(1)==[1]
    assert is_str(1)==False and is_str(u'X')==True

def test_open_struct():
    o = OpenStruct(b=2)
    o.a = 3
    o['c'] = 4
    assert o.b==2
    assert o.a==3
    assert o['c']==4
    assert o.to_dict() == {'a': 3, 'b': 2, 'c': 4}
    assert sorted(o.keys()) == ['a', 'b', 'c']
    assert sorted(o.items()) == [('a', 3), ('b', 2), ('c', 4)]
    assert sorted(o) == ['a', 'b', 'c']
    assert sorted(o.values()) == [2,3,4]
    assert dict(o)=={'a': 3, 'b': 2, 'c': 4}
