import urllib2
import os

from zstock.conf import *
from zstock.utils.path import *
from zstock.utils.log import *
from zstock.plot.ofc2 import *

class SimpleHTML(object):
    uniq_id = 0
    def __init__(self):
        self.head = []
        self.body = []

    def tag(self, t, text=None):
        if isinstance(text, list):
            text = '\n'.join(text)
        if not t:
            return text
        elif text is None:
            return "<%s>" % t
        else:
            return "<%s>%s</%s>" % (t, text, t)

    def render_html(self, only_body=True):
        if only_body:
            return self.tag(None, self.body)
        else:
            return self.tag('html', self.tag('head',self.head) + self.tag('body', self.body))

    def write(self, filename):
        f = open(filename, 'w')
        f.write(self.render_html())
        f.close()

    def append(self, text):
        if isinstance(text, SimpleHTML):
            self.head += text.head
            self.body += text.body
        elif isinstance(text, (tuple,list)):
            self.head.append(text[0])
            self.body.append(text[1])
        else:
            self.body.append(text)
        return self

    def table(self, info, schema):
        self.body.append(make_html_table(info, schema))
        return self

    def ofc_chart(self, chart, *args, **kwargs):
        return self.append(ofc_chart_html(chart, *args, **kwargs))

    def ofc_chart_list(self, *args, **kwargs):
        gs = []
        for g,xy in args:
            gs.append(ofc_chart(g,xy))
        return self.ofc_chart(gs, **kwargs)

    def __getattr__(self, attr):
        def f(*arg, **kwargs):
            if attr in 'render'.split():
                raise Exception('tag <%s> maybe incorrect' % attr)
            return self.append(self.tag(attr, *arg, **kwargs))
        return f

def html_tag(tag, text):
    return '<%s>%s</%s>' % (tag, text, tag)

def make_html_table(info, schema):
    t = "<table class=sortable border=1 cellspacing=0 cellpadding=4>"
    t += "\n<tr>"
    for s in schema:
        t += "<th>%s" % s
    for r in info:
        t += "\n<tr>"
        if isinstance(r,dict):
            for s in schema:
                t += "<td>%s" % (r.get(s) or '')
        else:
            for i in range(len(r)):
                t += "<td>%s" % r[i]
    t += "\n</table>"
    return t


