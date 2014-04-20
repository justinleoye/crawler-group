import sys
import zipfile
import os
import getopt
import shutil


def zip_file(file_from, file_to=None, del_source=True):
    if file_to is None:
        file_to = file_from + '.zip'
    f = zipfile.ZipFile(file_to, "w")
    f.write(file_from, os.path.basename(file_from), zipfile.ZIP_DEFLATED)
    f.close()
    if del_source:
        os.remove(file_from)

def normalize_zip_filename(filename, zip):
    if zip and not filename.lower().endswith('.zip'):
        filename += '.zip'
    return filename


def unzip(zipsource, encoding='cp936', 
        password=None, verbose=False, path=None, unzip_encoding='utf8'):
    try:
        f = zipfile.ZipFile(zipsource, 'r')
    except zipfile.BadZipfile:
        raise Exception("ERROR: File is broken zip or not a zip file")

    if password != None:
        f.setpassword(password)

    if path is not None:
        os.system('mkdir -p %s' % path)
    for fileinfo in f.infolist():
        try:
            filename = unicode(fileinfo.filename, encoding)
        except TypeError:
            filename = fileinfo.filename
        except Exception,e:
            raise e

        if path is not None:
            filename = os.path.join(path, filename)
        if unzip_encoding is not None:
            filename = filename.encode(unzip_encoding)
        if filename.endswith('/'):
            if not os.path.isdir(filename):
                os.mkdir(filename)
                if verbose:
                    print "Create : " + filename
        else:
            outputfile = open(filename, "wb")
            try:
                shutil.copyfileobj(f.open(fileinfo.filename), outputfile)
            except:
                raise Exception("ERROR: File is encrypted, password required for extraction (-p, --password)")
            if verbose:
                print "Extract: " + filename

