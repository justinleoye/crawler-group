import yaml
import jinja2
import os.path

from collections import defaultdict

from .type_utils import *
from .log_utils import *
from .path_utils import prepend_ext

class Loader(yaml.Loader):
    def __init__(self, stream, conf):
        self.conf = conf

        root = conf.get('root')

        if root is None:
            if hasattr(stream, 'name'):
                self.root = os.path.split(stream.name)[0]
            else:
                self.root = ''
        else:
            self.root = root

        self.template = conf.get('template')
        self.template_env = conf.get('template_env', {})

        if is_str(stream):
            content = stream
        else:
            content = stream.read()

        content = self.render(content)
        super(Loader, self).__init__(content)

    def render(self, content):
        if self.template == 'jinja':
            if not isinstance(content, unicode):
                content = content.decode('utf8')
            content = jinja2.Template(content).render(**self.template_env)
        elif self.template:
            raise Exception("template not supprted: %s" % self.template)
        return content

    def include(self, node):
        filename = self.construct_scalar(node)
        filename = os.path.join(self.root, filename)
        with open(filename, 'r') as f:
            content = self.render(f.read())

            conf = dict(self.conf)
            conf['root'] = os.path.dirname(filename)
            return load(content, **conf)

    def local_include(self, node):
        filename = self.construct_scalar(node)
        filename = os.path.join(self.root, filename)

        local_filename = prepend_ext(filename, '.local')
        if os.path.exists(local_filename):
            filename = local_filename
            DEBUG("[yaml_utils.local_include: %s" % filename)

        with open(filename, 'r') as f:
            content = self.render(f.read())

            conf = dict(self.conf)
            conf['root'] = os.path.dirname(filename)
            return load(content, **conf)

    def multi_include(self, node):
        r = None
        for filename in self.construct_sequence(node):
            filename = os.path.join(self.root, filename)

            with open(filename, 'r') as f:
                content = self.render(f.read())

                conf = dict(self.conf)
                conf['root'] = os.path.dirname(filename)
                x = load(content, **conf)
                if r is None:
                    r = x
                elif isinstance(r, list):
                    if not isinstance(x, list):
                        raise Exception("multi_include type differ")
                    r += x
                elif isinstance(r, dict):
                    if not isinstance(x, dict):
                        raise Exception("multi_include type differ")
                    r.update(x)
                else:
                    raise Exception("multi_include unknown type %s" % x.__class__)
        return r

Loader.add_constructor('!include:', Loader.include)
Loader.add_constructor('!local_include:', Loader.local_include)
Loader.add_constructor('!multi_include:', Loader.multi_include)


def load(x, **kwargs):
    return Loader(x, kwargs).get_data()

def json_to_yaml(d):
    import json
    if isinstance(d, (str, unicode)):
        d = json.loads(d)
    return yaml.safe_dump(d)

def dump_clean(x):
    """
    http://pyyaml.org/wiki/PyYAMLDocumentation

    default_style : indicates the style of the scalar. Possible values are None, '', '\'', '"', '|', '>'.
    default_flow_style :  indicates if a collection is block or flow. The possible values are None, True, False.
    canonical : if True export tag type to the output file
    indent :  sets the preferred indentation
    width : set the preferred line width
    allow_unicode : allow unicode in output file
    line_break : specify the line break you need
    encoding : output encoding, defaults to utf-8
    explicit_start : if True, adds an explicit start using "-"
    explicit_end: if True, adds an explicit end using "-"
    version : version of the YAML parser, tuple (major, minor), supports only major version 1
    tags : I didn't find any information about this parameter  and no time to test it
    """
    if isinstance(x, defaultdict):
        x = dict(x)
    return yaml.safe_dump(x, allow_unicode=True, indent=4)

def pretty_dump(x):
    import pyaml
    return pyaml.dump(x)

