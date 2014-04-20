
try:
    import pudb as pdb
except:
    import pdb

from pyutils.open_struct import OpenStruct

__all__ = [
    'SET_TRACE', 'SET_TRACE_', 
    'CLEAR_TRACE', 'CLEAR_TRACE_',
    'UNCLEAR_TRACE', 'UNCLEAR_TRACE_',
    'BREAK_POINT', 'BREAK_POINT_',
    'IN_DEBUG',
    'DebugInfo',
]

_clear_trace_level = 0
IN_DEBUG = False

class DebugInfo(OpenStruct):
    def __init__(self, *args, **kwargs):
        d = {
            'active': False,
            'auto_break': False
        }
        d.update(kwargs)
        super(DebugInfo, self).__init__(*args, **d)

def SET_TRACE(level=0):
    global IN_DEBUG
    if level >= _clear_trace_level:
        IN_DEBUG = True
        pdb.set_trace()

def BREAK_POINT():
    global IN_DEBUG
    if IN_DEBUG:
        pdb.set_trace()

def CLEAR_TRACE(level=1000000):
    global _clear_trace_level
    _clear_trace_level = level
    
def UNCLEAR_TRACE():
    global _clear_trace_level
    _clear_trace_level = 0

def _empty():
    pass

SET_TRACE_ = _empty
CLEAR_TRACE_ = _empty
UNCLEAR_TRACE_ = _empty
BREAK_POINT_ = _empty

