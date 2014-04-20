import math
import sys

import rpy2.robjects as robjects

from zstock.conf import *

"""
_ver = sys.version[:3]
if _ver=='2.5':
    import rpy2_py25.robjects as robjects
elif _ver=='2.6':
    import rpy2_py26.robjects as robjects
else:
    raise Exception("please install a rpy2 version for python %s" % _ver)
"""

r = robjects.r

FV = robjects.FloatVector
IV = robjects.IntVector
SV = robjects.StrVector

def RT(v):
    if isinstance(v, (list,tuple)):
        if len(v)==0:
            return FV([])
        elif isinstance(v[0], float):
            return FV(v)
        elif isinstance(v[0], int):
            return IV(v)
        elif isinstance(v[0], (str,unicode)):
            return SV(v)
    elif isinstance(v, unicode):
        return v.encode(DEFAULT_ENCODING)
    else:
        return v
def PT(v):
    if isinstance(v, (FV, IV, SV, robjects.RVector)):
        if len(v)==1:
            return v[0]
        else:
            return v
    else:
        return v

def r_method(fname):
    def inner(*args, **kwargs):
        fn = fname.replace('_','.')
        rargs = map(RT, args)
        rkwargs = {}
        for k, v in kwargs.iteritems():
            if v is not None:
                rkwargs[k.replace('_','.')] = RT(v)
        x = r[fn](*rargs, **rkwargs)
        return PT(x)
    return inner

def r_plot_method(fname):
    def inner(*args, **kwargs):
        if 'main' not in kwargs:
            kwargs['main'] = fname
        if 'xlab' not in kwargs:
            kwargs['xlab'] = 'x'
        if 'ylab' not in kwargs:
            kwargs['ylab'] = 'y'

        f = kwargs.get('filename')
        if f is not None:
            png_plot_open(f, kwargs.get('width'), kwargs.get('height'))
            del kwargs['filename']
            if 'width' in kwargs:
                del kwargs['width']
            if 'height' in kwargs:
                del kwargs['height']
            r_method(fname)(*args, **kwargs)
            png_plot_close()
        else:
            r_method(fname)(*args, **kwargs)
    return inner

def png_plot_open(f, width=None, height=None):
    from zstock.utils.path import mkdir_p
    from zstock.conf import DEFAULT_ENCODING
    if f is not None:
        mkdir_p(filename=f)
        r.png(f.encode(DEFAULT_ENCODING), 
                width=width or 800, height=height or 600)

def png_plot_close():
    r['dev.off']()

def create_matrix(recs, colname, rowname):
    vals = sum(recs, [])
    row = len(recs)
    col = len(colname)
    return r.matrix(FV(vals), nrow=row, ncol=col, byrow=True, 
            dimnames=r.list(SV(rowname), SV(colname)))

class RWrapper(object):
    def __init__(self):
        pass
    
    def __getattr__(self, a):
        if a=='r':
            return r
        elif globals().get(a):
            return globals()[a]
        elif a in 'plot hist plot3d lines'.split():
            return r_plot_method(a)
        else:
            return r_method(a)

    def __getitem__(self, a):
        return self.__getattr__(a)

    def __call__(self, *args, **kwargs):
        return r(*args, **kwargs)

R = RWrapper()

