
from collections import MutableMapping

class TransactionalDict(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.setup(*args, **kwargs)

    def setup(self, *args, **kwargs):
        #None is same to deleted
        self.in_transaction = False
        self.changed = False
        self.old_values = {}
        self.inserted = set()
        self.values = dict(*args, **kwargs)

    def clear(self):
        self.setup()

    def __repr__(self):
        return repr(self.values)

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        return iter(self.values)

    def ensure_in_transaction(self):
        if not self.in_transaction:
            raise Exception("not in transaction")

    def ensure_not_in_transaction(self):
        if self.in_transaction:
            raise Exception("already in transaction")

    def begin(self):
        self.ensure_not_in_transaction()
        self.in_transaction = True
        self.changed = False
        
    def commit(self):
        self.ensure_in_transaction()
        self.in_transaction = False
        self.old_values = {}
        self.inserted = set()

    def rollback(self):
        self.ensure_in_transaction()
        self.in_transaction = False

        for k,v in self.old_values.iteritems():
            self.values[k] = v

        for k in self.inserted:
            self.values.pop(k, None)

        self.old_values = {}
        self.inserted = set()

    def backup(self, key):
        if self.in_transaction:
            self.changed = True
            if not key in self.old_values:
                if not key in self.values:
                    self.inserted.add(key)
                elif not key in self.inserted:
                    self.old_values[key] = self.values[key]

    def __getitem__(self, key):
        return self.values[key]

    def __setitem__(self, key, value):
        self.backup(key)
        self.values[key] = value            

    def __delitem__(self, key):
        if not key in self.values:
            raise KeyError()
        self.backup(key)
        del self.values[key]



