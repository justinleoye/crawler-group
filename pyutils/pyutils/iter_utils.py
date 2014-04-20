from pyutils.log_utils import *

from itertools import *
import functools
import heapq
import operator
import collections

def concat(*args):
    for a in args:
        for s in a:
            for x in s:
                yield x

def ihead(iter, n):
    i = 0
    for x in iter:
        i += 1
        if i>n:
            break
        yield x

def ifirst(iter):
    y = None
    for x in iter:
        if y is None:
            y = x
    return y

def idecode(input, coding=None):
    raise Exception("not tested")
    if not coding:
        for x in input:
            yield x
        return
    if not isinstance(coding, (list,tuple)):
        coding = [coding]
    for s in input:
        for enc in coding:
            try:
                s = s.decode(enc)
                yield s
                break
            except:
                ERROR('encoding error: %s %s' % (enc, s))

def iencode(input, coding=None):
    for s in input:
        if coding is not None:
            s = s.encode(coding)
        yield s

def itrim(input, char='\n'):
    for x in input:
        yield x.rstrip(char)

def slice_iter(iterable, size):
    sourceiter = iter(iterable)
    while True:
        batchiter = islice(sourceiter, size)
        yield chain([batchiter.next()], batchiter)

def partial_sort(data, length, **kwargs):
    for s in slice_iter(data, length):
        a = sorted(s, **kwargs)
        if len(a)==0:
            break
        for e in a:
            yield e

# data is (key,value) pair
def partial_reduce(data, len, reduce, 
        key_func=operator.itemgetter(0), val_func=operator.itemgetter(1)):
    sdata = partial_sort(data, key=key_func)
    for k,g in igroup(sdata, key_func):
        yield k, reduce(imap(g, val_func))

#sort a nearly-sorted stream
def isort(stream, chunk=1024, key=None):
    #TODO
    raise Exception("TODO")

def ipeekn(iterable, n):
    it = iter(iterable)
    peek = []
    for i in range(n):
        try:
            peek.append(next(it))
        except StopIteration:
            break
    return peek, chain(peek, it)

def ipeek(iterable):
    r = ipeekn(iterable, 1)
    n = len(r[0])
    if n==1:
        return r[0][0], r[1]
    elif n==0:
        return None, r[1]
    else:
        return r

def itranspose(iterable):
    it = iter(iterable)
    first, it = ipeek(it)
    if first is None:
        return tuple()

    n = len(first)

    deques = [collections.deque() for i in range(n)]
    def gen(dq):
        while True:
            if not dq:
                x = next(it)
                for i in range(n):
                    deques[i].append(x[i])
            yield dq.popleft()
    return tuple(gen(d) for d in deques)

def imerge_t(iterable):
    channels = itranspose(iterable)
    return imerge(*channels)

def ijoin(*iterables):
    '''Join multiple sorted inputs into a single sorted output.

    >>> list(ijoin([(1,'x'),(3,'y')], [], [(1,10), (2, 20), (3,30)], [(2, 0.5), (4, 0.3)]))
    [(1, ['x', None, 10, None]), (2, [None, None, 20, 0.5]), (3, ['y', None, 30, None]), (4, [None, None, None, 0.3])]

    '''

    itrs = []
    n = len(iterables)
    for i in range(n):
        f = lambda i, key, *args: [key, i] + list(args)
        itrs.append(starmap(functools.partial(f, i), iterables[i]))

    s = imerge(*itrs)
    for k, g in igroupby(s, lambda x: x[0]):
        r = [None]*n
        for x in g:
            r[x[1]] = x[2]
        yield k, r

def imerge(*iterables):
    '''Merge multiple sorted inputs into a single sorted output.

    Equivalent to:  sorted(itertools.chain(*iterables))

    >>> list(imerge([1,3,5,7], [0,2,4,8], [5,10,15,20], [], [25]))
    [0, 1, 2, 3, 4, 5, 5, 7, 8, 10, 15, 20, 25]

    '''
    heappop, siftup, _StopIteration = heapq.heappop, heapq._siftup, StopIteration

    h = []
    h_append = h.append
    for it in map(iter, iterables):
        try:
            next = it.next
            h_append([next(), next])
        except _StopIteration:
            pass
    heapq.heapify(h)

    while 1:
        try:
            while 1:
                v, next = s = h[0]      # raises IndexError when h is empty
                yield v
                s[0] = next()           # raises StopIteration when exhausted
                siftup(h, 0)            # restore heap condition
        except _StopIteration:
            heappop(h)                  # remove empty iterator
        except IndexError:
            return

def igroupby(stream, key_func):
    first = True
    k0 = None
    g = None
    for x in stream:
        k = key_func(x)
        if first or k!=k0:
            first = False
            if g:
                yield k0,g
            g = []
            k0 = k
        g.append(x)
    if g:
        yield k0,g


if __name__ == '__main__':
    import doctest
    doctest.testmod()

