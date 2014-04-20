
from pyutils.iter_utils import *

def echo_generator():
    r = None
    while True:
        r = (yield r)
        print 'ECHO %s' % r

def print_filter(x):
    for r in x:
        print 'PRINT %s' % r
        yield '==%s' % r

def test_echo_generator():
    g = echo_generator()
    g.next()
    g.send('ABC')

    f = print_filter(g)

    print 'main %s' % g.send('123')
    print 'main %s' % g.send('abc')

    i = 0
    for x in f:
        print 'main== %s' % x
        g.send(i*100)
        i += 1
        if i>3:
            g.close()



def print_generator():
    while True:
        print (yield 123)
        print (yield '==')
        print (yield '--')

def test_generator():
    a = print_generator()
    print a.next()
    print a.send("hello")
    print a.send("world")
    print a.send("test")

def test_ipeek():
    a = xrange(10)
    x, y = ipeekn(a, 2)
    print x, list(y)

def test_imerge_t():
    a = [
        [3, 2, 1],
        [4, 6, 5],
        [7, 8, 9],
        [15, 14, 11],
    ]

    a_t = [
        [3, 4, 7, 15],
        [2, 6, 8, 14],
        [1, 5, 9, 11]
    ]

    b = itranspose(a)
    b = [list(x) for x in b]
    assert b==a_t

    s = imerge_t(a)
    s = list(s)
    assert s==[1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 14, 15]



if __name__ == '__main__':
    test_echo_generator()
    #test_generator()
    #test_ipeek()
    #test_imerge_t()

