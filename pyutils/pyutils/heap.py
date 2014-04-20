from heapq import *

class HeapQueue(object):
    def __init__(self):
        self.heap = []

    def empty(self):
        return len(self.heap)==0

    def put(self, x):
        heappush(self.heap, x)

    def get(self):
        return heappop(self.heap)

    def top(self):
        return self.heap[0]

    def __len__(self):
        return len(self.heap)

    def __iter__(self):
        return iter(self.heap)

    def topn(self, n):
        if n > len(self.heap):
            n = len(self.heap)

        x = list(self.heap)
        return [heappop(x) for i in range(n)]
            
    def clear(self):
        self.heap = []
        

class TopNQueue(object):
    def __init__(self, n):
        self.n = n
        self.q = PriorityQueue()
        self.qn = PriorityQueue(maxsize=n)

    def put(self, x):
        self.q.put(x)
        self.qn.put(x)
        
    def empty(self):
        return self.q.empty()

    def get(self):
        raise Exception("get is not supported for TopNQueue")

    def top(self):
        if self.q.empty():
            return None
        return self.q.queue[0]

    def topn(self, n):
        return sorted(self.qn.queue)[:n]

