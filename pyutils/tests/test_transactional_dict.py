from pyutils import *
from pyutils.transactional_dict import *

def test_transactional_dict():
    d = TransactionalDict()
    d.begin()
    d[3] = 30
    d[2] = 20
    d.commit()
    assert d == {3: 30, 2:20}

    d.begin()
    d[3] = 3
    d[2] = 100
    d[3] = 300
    d[5] = 50
    d[6] = 60
    del d[2]
    assert not 2 in d
    assert d.get(2) == None
    assert d[3] == 300
    del d[6]
    assert not 6 in d
    d.rollback()
    assert d == {3: 30, 2:20}


if __name__ == '__main__':
    test_transactional_dict()

