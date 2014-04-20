import logging
import os
import sys
import traceback
import inspect

from colorama import Fore, Back, Style
#from colorlog import ColoredFormatter

from sys import version_info
from logging import Formatter
from colorlog.escape_codes import escape_codes

"""
http://www.python.org/dev/peps/pep-0008/
_single_leading_underscore: weak "internal use" indicator. E.g. from M import * does not import objects whose name starts with an underscore.
"""

__all__ = """
    INFO ERROR WARN DEBUG DEBUG_SYS DEBUG2 DEBUG3 MSG
    INFO_ ERROR_ WARN_ DEBUG_ MSG_
    LOG

    MARKER MARK MARK_ MARKER_

    EXCEPTION EXCEPTION_
    TMP_DEBUG TMP_DEBUG_

    SET_DEBUG RESET_LOG_LEVEL
""".split()


# The default colors to use for the debug levels
default_log_colors =  {
	'DEBUG':    'white',
	'INFO':     'green',
	'WARNING':  'yellow',
	'ERROR':    'red',
	'CRITICAL': 'bold_red',
}

def caller_name(skip=2):
    """Get a name of a caller in the format module.class.method
    
       `skip` specifies how many levels of stack to skip while getting caller
       name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.
       
       An empty string is returned if skipped levels exceed stack height
    """
    stack = inspect.stack()
    start = 0 + skip
    if len(stack) < start + 1:
      return ''
    parentframe = stack[start][0]    
    
    name = []
    module = inspect.getmodule(parentframe)
    # `modname` can be None when frame is executed directly in console
    # TODO(techtonik): consider using __main__
    if module:
        name.append(module.__name__)
    # detect classname
    if 'self' in parentframe.f_locals:
        # I don't know any way to detect call from the object method
        # XXX: there seems to be no way to detect static method call - it will
        #      be just a function call
        name.append(parentframe.f_locals['self'].__class__.__name__)
    codename = parentframe.f_code.co_name
    if codename != '<module>':  # top level usually
        name.append( codename ) # function or a method
    del parentframe
    return ".".join(name)

class ColoredFormatter (Formatter):
    """    A formatter that allows colors to be placed in the format string, intended to help in creating prettier, more readable logging output. """

    def __init__ (self, format, datefmt=None, log_colors=default_log_colors, reset=True, style='%'):
        """
        :Parameters:
        - format (str): The format string to use
        - datefmt (str): A format string for the date
        - log_colors (dict): A mapping of log level names to color names
        - reset (bool): Implictly appends a reset code to all records unless set to False
        - style ('%' or '{' or '$'): The format style to use. No meaning prior to Python 3.2.
        
        The ``format``, ``datefmt`` and ``style`` args are passed on to the Formatter constructor.
        """
        if version_info > (3, 2):
            super(ColoredFormatter, self).__init__(format, datefmt, style=style)
        elif version_info > (2, 7):
            super(ColoredFormatter, self).__init__(format, datefmt)
        else:
            Formatter.__init__(self, format, datefmt)
        self.log_colors = log_colors
        self.reset = reset

    def format (self, record):
        # Add the color codes to the record
        record.__dict__.update(escape_codes)

        # If we recognise the level name,
        # add the levels color as `log_color`
        if record.levelname in self.log_colors:
            color = self.log_colors[record.levelname]
            record.log_color = escape_codes[color]
        else:
            record.log_color = ""

        #NOTE: caller_name is very slow
        #record.__dict__['caller_name'] = caller_name(9)
        record.__dict__['abbr_levelname'] = record.levelname[0]
        record.__dict__['pathname2'] = '.'.join(record.pathname.split('/')[-2:]).rstrip('.py')

        # Format the message
        if version_info > (2, 7):
            message = super(ColoredFormatter, self).format(record)
        else:
            message = Formatter.format(self, record)

        # Add a reset code to the end of the message (if it wasn't explicitly added in format str)
        if self.reset and not message.endswith(escape_codes['reset']):
            message += escape_codes['reset']

        return message

colored_formatter = ColoredFormatter(
        #"%(asctime)s %(levelname)5s %(filename)64s%(lineno)4d %(log_color)s%(message)s%(reset)s",
        "%(green)s%(asctime)s %(white)s%(pathname2)32s%(cyan)s%(lineno)4d %(log_color)s[%(abbr_levelname)s] %(message)s%(reset)s",
        datefmt="%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG':    'bold_green',
            'INFO':     'bold_cyan',
            'WARNING':  'bold_yellow',
            'ERROR':    'bold_red',
            'CRITICAL': 'bold_red',
        }
)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(colored_formatter)

logger = logging.getLogger()
logger.addHandler(stream_handler)

INFO = logger.info
ERROR = logger.error
WARN = logger.warn
DEBUG = logger.debug
DEBUG_SYS = logger.warn
DEBUG2 = logger.warn
DEBUG3 = logger.error
TMP_DEBUG = logger.debug

LAST_LOG_LEVEL = None
LOG_LEVEL = logger.getEffectiveLevel()
IS_DEBUG_LEVEL = False

def SET_DEBUG(value=True):
    global LAST_LOG_LEVEL, LOG_LEVEL, IS_DEBUG_LEVEL
    LAST_LOG_LEVEL = LOG_LEVEL
    if value:
        LOG_LEVEL = logging.DEBUG
    else:
        LOG_LEVEL = logging.WARN
    logger.setLevel(LOG_LEVEL)

    r = IS_DEBUG_LEVEL
    IS_DEBUG_LEVEL = value
    return r

SET_DEBUG()

def RESET_LOG_LEVEL():
    logger.setLevel(LAST_LOG_LEVEL)

def EXCEPTION(e):
    exstr = traceback.format_exc()
    ERROR(exstr)

def _empty(*args, **kwargs): pass

DEBUG_ = INFO_ = WARN_ = ERROR_ = MSG_ = _empty
EXCEPTION_ = TMP_DEBUG_ = MARKER_ = MARK_ = _empty

def MARKER(c='=', n=128):
    MSG('Red', c*n)

MARK = MARKER

def MSG(color, *args):
    cs = 'RED GREEN YELLOW BLUE MAGENTA CYAN WHITE BLACK'.split()

    x = color.upper()
    msg = ' '.join(map(str,args))
    for c in cs:
        if c[:len(x)]==x:
            msg = Fore.__dict__[c] + msg
            if color[0].isupper():
                msg = Style.BRIGHT + msg
    msg += Fore.RESET + Style.RESET_ALL
    sys.stderr.write(msg+'\n')
    
def LOG(*args):
    frame,filename,line_number,function_name,lines,index=\
        inspect.getouterframes(inspect.currentframe())[1]
    MSG('BLUE', '%s:%s:%s' % (filename, line_number, function_name))
    MSG('MAGENTA', *args)

def ColoredWriter(object):
    cs = 'RED GREEN YELLOW BLUE MAGENTA CYAN WHITE BLACK'.split()

    def __init__(self, out, auto_newline=True):
        self.out = out
        self.auto_newline = auto_newline
    
    def write_auto_newline(self):
        if self.auto_newline:
            self.out.write('\n')

    def write_color(self, color, *args):
        msg = ' '.join(map(str, args))
        msg = Fore.__dict__[color] + msg
        if color[0].isupper():
            msg = Style.BRIGHT + msg

        self.out.write(msg)
        self.write_auto_newline()

    def write(self, *args):
        self.write_color('white', *args)

    def __getattr__(self, attr):
        def f(*args, **kwargs):
            self.write_color(attr, *args, **kwargs)
        return f


if __name__ == '__main__':
    MSG('r', 'test red')
    MSG('G', 'test bright green')


    

