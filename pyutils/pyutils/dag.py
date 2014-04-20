from pyutils import *

from collections import defaultdict, Hashable

class Graph(object):
    def __init__(self):
        self.out = defaultdict(set)
        self.node = defaultdict()

    def __repr__(self):
        edges = []
        for v,e in self.out.items():
            a = [ self.get_node(v), '->' ]
            for x in e:
                a.append(self.get_node(x))
            edges.append(' '.join(a))

        return """
        Graph:
            edges: %s
            nodes: %s
        """ % (edges, list(self.node.values()))

    def get_id(self, x):
        #NOTE: id('ab')!=id(('ab'*100)[:2])
        if isinstance(x, Hashable):
            return x
        else:
            return id(x)

    def get_node_id(self, x):
        nid = self.get_id(x)
        if not nid in self.node:
            raise Exception("task not exists: %s" % str(x))
        return nid

    def get_node(self, aid):
        return self.node.get(aid)

    def get_node_list(self, ids):
        for x in ids:
            yield self.get_node(x)

    def edge_added(self, aid, bid):
        pass

    def node_added(self, nid):
        pass

    def node_deleted(self, nid):
        pass

    def edge_deleted(self, aid, bid):
        pass

    def graph_created(self):
        pass

    #add edge a->b
    def add_edge(self, a, b):
        aid = self.add_node(a, False)
        bid = self.add_node(b, False)
        if not bid in self.out[aid]:
            self.out[aid].add(bid)
            self.edge_added(aid, bid)
    
    def del_edge(self, aid, bid):
        if bid in self.out[aid]:
            self.out[aid].remove(bid)
            self.edge_deleted(aid, bid)

    def add_node(self, a, update=True):
        aid = self.get_id(a)
        if update or self.get_node(aid) is None:
            self.node[aid] = a
            self.node_added(aid)
        return aid

    def del_node(self, nid, remove_edge_only=False):
        for x in list(self.out[nid]):
            self.del_edge(nid, x)

        if not remove_edge_only:
            del self.node[nid]
            del self.out[nid]

        self.node_deleted(nid)

    def clear(self):
        self.out.clear()
        self.node.clear()
    
    def lock(self):
        pass

    def unlock(self):
        pass


class DAG(Graph):
    def __init__(self):
        super(DAG, self).__init__()
        self.ideg = defaultdict(int)
        self.ready = set()
        self.run = set()
        self.done = set()

    def __repr__(self):
        ready = map(self.get_node, self.ready)
        run = map(self.get_node, self.run)
        done = map(self.get_node, self.done)
        ideg = [(self.get_node(x), n) for x,n in self.ideg.items()]
        return """
        DAG:
            ready: %s
            done: %s
            run: %s
            ideg: %s
            %s
        """ % (ready, done, run, ideg, Graph.__repr__(self))

    def clear(self):
        super(DAG, self).clear()
        self.ideg.clear()
        self.ready.clear()
        self.run.clear()
        self.done.clear()

    def node_added(self, nid):
        self.ready.add(nid)

    def node_deleted(self, nid):
        pass

    def edge_deleted(self, aid, bid):
        self.ideg[bid] -= 1
        if not self.ideg[bid]:
            self.ready.add(bid)

    def edge_added(self, aid, bid):
        self.ideg[bid] += 1
        self.ready.discard(bid)

    def task_done(self, task):
        nid = self.get_node_id(task)
        #task may be done without run
        self.run.discard(nid)
        self.ready.discard(nid)
        self.done.add(nid)
        #SET_TRACE()

        self.del_node(nid, remove_edge_only=True)

    def has_ready_task(self):
        return len(self.ready)>0

    def ready_tasks(self):
        return [self.get_node(nid) for nid in self.ready]

    def run_task(self, task):
        nid = self.get_node_id(task)
        self.ready.remove(nid)
        self.run.add(nid)



