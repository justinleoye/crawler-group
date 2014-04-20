from datetime import *

from pyutils import *
from pyutils.datetime_utils import *

def test_datetime_cmp():
    f = compare_datetime
    print f('12:01', datetime.now())
    print f(datetime.now(), '12:01:00')
    print f(datetime.now(), '2090-01-01 12:01:00')
    print f(datetime.now(), '2090-01-01')
    print f('23:01', datetime.now())

if __name__ == '__main__':
    test_datetime_cmp()
