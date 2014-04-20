import os
from collections import defaultdict
import types
try:
    import pudb as pdb
except:
    import pdb

import pyutils.debug_utils
from pyutils.func_utils import BindFirstFunction
from pyutils.log_utils import *
from pyutils.type_utils import *
from pyutils.debug_utils import DebugInfo, SET_TRACE

debug = DebugInfo(active=os.environ.get('OBSERVER_DEBUG')=='1')

_debug_print_level = 0

class StopFurtherHandler(Exception):
    pass

class StopParentHandler(Exception):
    pass

class StopFurtherProcessing(Exception):
    pass

class StopParentProcessing(Exception):
    pass


def observer_handler(f):
    def g(*args, **kwargs):
        if debug.active:
            DEBUG("call %s with args %s %s" % (f.__name__, args, kwargs))
        r = f(*args, **kwargs)
        if debug.active:
            DEBUG("call %s return %s" % (f.__name__, r))
        return r
    return g

class Event(object):
    def __init__(self, name=None, sender=None, topic_key=None, full_name=None):
        self.name = name
        self.full_name = full_name
        self.sender = sender
        self.topic_key = topic_key
        self.handlers = []
        self.handler_names = []
        self.channels = defaultdict(list)

        #for speed up many empty event slots
        self.is_empty = True
    
    def has_listener(self):
        if self.is_empty:
            return False
        if len(self.handlers)>0:
            return True
        for topic, listeners in self.channels.iteritems():
            if len(listeners)>0:
                return True
        return False

    def dispatch_by(self, topic_key):
        self.topic_key = topic_key

    def get_handler(self, handler):
        if isinstance(handler, ObserverMixin) and self.name is not None:
            handler = handler.get_event_handler('process_' + self.name)
        return handler

    def get_handlers(self, handlers):
        r = []
        for h in get_list(handlers):
            x = self.get_handler(h)
            if x is not None:
                r.append(x)
        return r

    def subscribe(self, handler, topic=None, name=None):
        self.is_empty = False
        self.handler_names.append(name)
        for handler in self.get_handlers(handler):
            if topic is None:
                self.handlers.append(handler)
            else:
                self.channels[topic].append(handler)
        return self
    
    def unsubscribe(self, handler, topic=None):
        for handler in self.get_handlers(handler):
            if topic is None:
                self.handlers.remove(handler)
            else:
                self.channels[topic].remove(handler)
        return self
    
    def fire(self, *args, **kwargs):
        if self.topic_key is not None:
            topic = args[0].get(self.topic_key)
        else:
            topic = None

        handlers = self.handlers
        if topic is not None:
            if topic in self.channels:
                handlers = self.handlers + self.channels[topic]

        if debug.active and len(handlers)>0:
            DEBUG_('fire: %s %s, handlers: %d' % (self.sender.__class__.__name__, self.full_name, len(handlers)))
            #INFO_('handlers: %s' % handlers)

        for handler in handlers:
            try:
                handler(*args, **kwargs)
            except StopFurtherHandler:
                break
            except StopParentHandler:
                raise StopFurtherHandler()
            except TypeError, e:
                ERROR('%s: %s %s %s' % (e, handler, args, kwargs))
                raise
                

    add = subscribe
    remove = unsubscribe

    notify = subscribe
    unnotify = unsubscribe

    connect = subscribe
    disconnect = unsubscribe

    emit = fire

    __iadd__ = subscribe
    __isub__ = unsubscribe
    __call__ = fire

class ObserverMixin:
    def _process_event(self, event, *args, **kwargs):
        global  _debug_print_level
        is_event_slot = True
        for p in ['before_', 'pre_',  'handle_', 'on_',  'after_', 'post_']:
            is_event_slot = not is_event_slot
            a = p + event

            if is_event_slot:
                if not a in self.__dict__:
                    continue
            elif not hasattr(self, a):
                continue

            f = getattr(self, a)
            #f = self.get_event_handler(a, None)

            if f is None or (is_event_slot and f.is_empty):
                continue

            if debug.active:
                prefix = ' ' * _debug_print_level
                msg = '%s%s.%s' % (prefix, self.__class__.__name__, a)
                if p in ['before_', 'handle_', 'after_']:
                    INFO(msg)
                    DEBUG('%s    %s %s' % (prefix, args, kwargs))
                elif p=='on_':
                    DEBUG_(msg)
                #DEBUG('  %s %s' % (args, kwargs))
                if p=='handle_':
                    if pyutils.debug_utils.IN_DEBUG  and debug.auto_break:
                        if not event in debug.ignored_events:
                            pdb.set_trace()
                _debug_print_level += 1
            try:
                f(*args, **kwargs)
            except StopFurtherProcessing:
                if debug.active:
                    DEBUG("StopFurtherProcessing %s" % a)
                break
            except StopParentProcessing:
                if debug.active:
                    DEBUG("StopParentProcessing %s" % a)
                raise StopFurtherProcessing()
            except TypeError, e:
                ERROR('%s: %s %s %s' % (e, f, args, kwargs))
                raise
            finally:
                _debug_print_level -= 1

    def has_listener(self, event):
        for p in ['on_', 'pre_', 'post_']:
            attr = getattr(self, p + event)
            if attr is not None and attr.has_listener():
                return True
        return False
        
    def create_event(self, event):
        #TODO:remove create_event
        return

        for p in ['on_', 'pre_', 'post_']:
            attr = p + event
            setattr(self, attr, Event(name=event, sender=self, full_name=attr))

        #setattr(self, 'process_' + event, types.MethodType(_process_event, self))

    def create_events(self, *events):
        for e in events:
            self.create_event(e)

    def _empty_hanlder(self, *args, **kwargs):
        pass

    def get_event_handler(self, attr, default=None):
        try:
            return getattr(self, attr)
        except AttributeError:
            return default
        
    def __getattr__(self, attr):
        #TODO peformance may not be good
        a = attr.split('_', 1)
        prefix = a[0]
        cls = self.__class__.__name__

        if prefix == 'process':
            DEBUG_('%s.%s' % (cls, attr))
            f = BindFirstFunction(self._process_event, attr[8:])
            setattr(self, attr, f)
            return f

        elif prefix in ['on', 'pre', 'post']:
            DEBUG_('%s.%s' % (cls, attr))
            event = a[1]
            e = Event(name=event, sender=self, full_name=attr)
            setattr(self, attr, e)
            return e
            
        raise AttributeError(attr)



