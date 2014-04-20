import sys
import traceback

def TRACE_BACK(e=None):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    b = traceback.format_tb(exc_traceback)
    return '\n'.join(b)
