import os
import re
import jinja2

try:
    import configure
except:
    configure = None

from pyutils.log_utils import *
from pyutils import yaml_utils, dict_utils, path_utils

def config_to_dict(c):
    if isinstance(c, configure.Configuration):
        r = {}
        for k in c:
            r[k] = config_to_dict(c[k])
        return r
    else:
        return c

def load_pkg_resource_config(pkg, resource, as_dict=True, **kwargs):
    import pkg_resources
    try:
        f = pkg_resources.resource_stream(pkg, resource)
    except IOError, e:
        return None

    config = yaml_utils.load(f, **kwargs)
    f.close()
    if not as_dict:
        cc = configure.Configuration
        config = cc.from_dict(config)
    return config

def load_config_from_package(pkg, filename):
    return load_pkg_resource_config(pkg, filename)

def load_config_from_packages(pkgs, filename):
    c = {}
    for p in pkgs:
        d = load_config_from_package(p, filename)
        if not d:
            continue
        dict_utils.recursive_merge(c, d)
    return c

def load_config_merged(conf_files, template=None, template_env=None, as_dict=False, root=None):
    confs = []
    for f in conf_files:
        if root is not None:
            f = os.path.join(root, f)
        if os.path.exists(f):
            INFO("loading config from file %s" % f)

            f = open(f, 'r')
            config = yaml_utils.load(f, template=template, template_env=template_env)
            f.close()
            confs.append(config)

    if confs:
        config = confs[0]
        for i in range(1, len(confs)):
            config.update(confs[i])

        if not as_dict:
            config = configure.Configuration.from_dict(config)

        return config
    return None

def get_local_conf_file(c):
    return path_utils.prepend_ext(c, '.local')

def load_config(conf_file, *args, **kwargs):
    conf_files = [conf_file, get_local_conf_file(conf_file)]
    return load_config_merged(conf_files, *args, **kwargs)

def load_project_config(project, conf_file, template=None, template_env=None,
as_dict=False, default_conf_file=None, local_conf_file=None, conf_path=None):
    locs = [ 
        conf_path,
        '', # os.path.join('', 'abc')=='abc'
        os.curdir, 
        os.path.join(os.curdir, project), 
        os.path.join(os.curdir, 'etc', project),
        os.path.join(os.path.expanduser("~"), 'etc', project),
        os.path.expanduser("~"), 
        os.path.join("/etc", project), 
        os.environ.get("%s_CONF" % project.upper()) 
    ]
    
    DEBUG('search config file %s in %s' % (conf_file, locs))

    cc = configure.Configuration

    #conf precedence: local > conf > default
    conf_files = []
    if default_conf_file:
        conf_files.append(default_conf_file)
    conf_files.append(conf_file)
    if local_conf_file:
        conf_files.append(local_conf_file)

    for loc in locs:
        if loc is None:
            continue
        
        fs = [os.path.join(loc, f) for f in conf_files]
        c = load_config_merged(fs, template=template, template_env=template_env, as_dict=as_dict)
        if c is not None:
            return c

        #TODO DELETE
        """
        confs = []
        for cf in conf_files:
            f = os.path.join(loc, cf)
            if os.path.exists(f):
                INFO("loading config from file %s" % f)

                f = open(f, 'r')
                config = yaml_utils.load(f, template=template, template_env=template_env)
                f.close()
                confs.append(config)

        if confs:
            config = confs[0]
            for i in range(1, len(confs)):
                config.update(confs[i])

            if not as_dict:
                config = cc.from_dict(config)

            return config
        """

    WARN('no config file found for %s:%s' % (project, conf_file))
    return None

"""
    conf.not_exists_key_1.not_exists_key_2 != None
    conf.not_exists_key_1['not_exists_key_2'] == None
    conf.not_exists_key_1.get('not_exists_key_2', 'default') == 'default'
"""
class Config(object):
    def __init__(self, values={}, is_null=False, default=None):
        self.__dict__.update(dic)
        self.default = default
        self.is_null = is_null

    def __getattr__(self, i):
        if not self.is_null and i in self.__dict__:
            return self.__dict__[i]
        else:
            return Config(is_null=True, default=default)

    def __setattr__(self,i,v):
        if i in self.__dict__:
            self.__dict__[i] = v
        else:
            self.__dict__.update({i:v})
        return v # i like cascates :)
        
    def get(key, default):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return default
        
    def __getitem__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return None

    def __setitem__(self, key, value):
        self.__dict__[key] = value
        return value

    def to_dict(self):
        return dict(self.__dict__)

    def get_dict(self):
        return self.__dict__

