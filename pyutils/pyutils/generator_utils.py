from itertools import *
import operator
import collections

from .type_utils import get_list
from .iter_utils import *

"""
import Queue, threading
class ConsumerThread(threading.Thread):
    def __init__(self,target):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.in_queue = Queue.Queue()
        self.ret_queue = Queue.Queue()
        self.target = target
        self.closed = False
        self.error = False

    def close(self):
        if self.error:
            return
        self.in_queue.join()
        self.closed = True
        self.send(None)

    def send(self,item):
        self.in_queue.put(item)

    def generate(self):
        while True:
            item = self.in_queue.get()
            if item is None and self.closed:
                break
            yield item
            self.in_queue.task_done()

    def result(self):
        if not hasattr(self, '_result'):
            self._result = self.ret_queue.get()
        return self._result

    def run(self):
        try:
            input = self.generate()
            output = self.target(input)
            self.ret_queue.put(output)
        except:
            while True:
                try:
                    self.in_queue.get_nowait()
                    self.in_queue.task_done()
                except:
                    break
            self.error = True
            raise
            

def broad_cast_old(source, consumers):
    consumer_threads = []
    for c in consumers:
        th = ConsumerThread(c)
        consumer_threads.append(th)
        th.start()
    for item in source:
        for t in consumer_threads:
            t.send(item)
    for t in consumer_threads:
        t.close()
    return [ t.result() for t in consumer_threads ]
"""


def mytee(iterable, n=2):
    it = iter(iterable)
    deques = [collections.deque() for i in range(n)]
    lock = threading.Lock()
    def gen(mydeque):
        while True:
            if not mydeque:
                try:
                    lock.acquire()
                    newval = it.next()
                    lock.release()
                except:
                    lock.release()
                    break
                for d in deques:
                    d.append(newval)
            yield mydeque.popleft()
    return tuple(gen(d) for d in deques)

def broad_cast(source, consumers):
    n = len(consumers)
    if n==0:
        return []
    if n==1:
        return [consumers[0](source)]

    # don't use thread when data is small
    source = list(source)
    if len(source)<10000:
        result = []
        for c in consumers:
            result.append(c(source))
        return result

    #stream_list = tee(source, n)
    #stream_list = mytee(source, n)
    stream_list = [source]*n

    result_queue = Queue.Queue()
    def consumer_thread(id):
        ret = consumers[id](stream_list[id])
        result_queue.put([id, ret])

    consumer_threads = []
    for i in range(n):
        t = threading.Thread(target=consumer_thread, args=[i])
        t.start()
        consumer_threads.append(t)

    for t in consumer_threads:
        t.join()
    
    results = [None] * n
    while True:
        try:
            id, ret = result_queue.get_nowait()
            results[id] = ret
        except:
            break
    return results

