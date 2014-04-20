import os
import time
import zipfile

from pyutils import *
from pyutils.sleep_utils import sleep
from .path_utils import *

from .generator_utils import idecode, itrim

def ensure_file_path(f):
    p = os.path.dirname(f)
    if p:
        mkdir_p(p)

def open_file_force(f, *args, **kwargs):
    p = os.path.dirname(f)
    if p:
        mkdir_p(p)
    return open(f,*args, **kwargs)

def zip_file(file_from, file_to=None, del_source=True):
    import zipfile
    if file_to is None:
        file_to = file_from + '.zip'
    f = zipfile.ZipFile(file_to, "w")
    f.write(file_from, os.path.basename(file_from), zipfile.ZIP_DEFLATED)
    f.close()
    if del_source:
        os.remove(file_from)

def read_from_file(filename, encoding=None):
    return ''.join(read_lines_from_file(filename, encoding))

def read_lines_from_file(filename, encoding=None, trim=False):
    #zip file
    if filename.lower().endswith('.zip'):
        def f():
            try:
                DEBUG_('[zipfile] open')
                root = zipfile.ZipFile(filename, "r")
                try:
                    for name in root.namelist():
                        if name.endswith('/'):
                            continue
                        h = root.open(name)
                        for line in h:
                            yield line
                        h.close()
                finally:
                    DEBUG_('[zipfile] close')
                    root.close()
            except Exception, e:
                ERROR(e)
                sleep(3, 'read_lines_from_file')
        x = f()
    #normal file
    else:
        h = open(filename)
        try:
            x = list(h)
        finally:
            h.close()

    if trim:
        x = itrim(x)

    if encoding is not None:
        x = idecode(x, encoding)

    return x

def read_table_from_file(filename, skip=None, sep="\t", mapper=None, encoding=None):
    x = read_lines_from_file(filename, encoding)

    if skip is not None:
        x = islice(x, skip, None)

    x = imap(lambda a: a.strip('\n'), x)

    if sep!='':
        x = imap(lambda a: a.split(sep), x)

    if mapper is not None:
        x = list_imap(x, mapper)

    return x

def read_from_csv_file(filename, skip=1, **kwargs):
    return read_from_file(filename, skip=skip, **kwargs)

def write_lines_to_zipfile(input, filename, auto_skip=False, encoding='utf8', origin_filename=None):
    if auto_skip and file_exists(filename):
        return

    if origin_filename is None:
        origin_filename = filename.rstrip('.zip')

    mkdir_p(filename=filename)
    f = zipfile.ZipFile(filename, "w")
    fn = os.path.basename(origin_filename)
    if encoding is not None and isinstance(fn, unicode):
        fn = fn.encode(encoding)
    s = ''.join(input)
    f.writestr(fn, s)
    f.close()

def write_lines_to_file(input, filename, zip=False, auto_skip=False, **kwargs):
    if auto_skip and file_exists(filename):
        return
    if zip:
        if not filename.lower().endswith('.zip'):
            filename += '.zip'
        write_lines_to_zipfile(input, filename, auto_skip, **kwargs)
    else:
        f = open_file_force(filename, 'wb')
        for s in input:
            f.write(s)
        f.close()

def write_to_file(content, *args, **kwargs):
    return write_lines_to_file([content], *args, **kwargs)

def write_stream_to_file(filename, stream, serializer):
    n = 0
    f = open_file_force(filename, 'wb')
    for x in stream:
        s = serializer.dumps(x)
        f.write(s.encode('utf8')+'\n')
        n += 1
    f.close()
    return n



