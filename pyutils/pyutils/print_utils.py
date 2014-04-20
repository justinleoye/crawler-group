import sys
from pprint import pprint

def print_list(a, p=sys.stdout.write):
    p('---- [%d]\n' % len(a))
    for x in a:
        p('  - %s\n' % x)

def print_dict(a, p=sys.stdout.write):
    p('---- {%d}\n' % len(a))
    for k,v in a.iteritems():
        p('  %10s: %s\n' % (k,v))

def to_pretty_print(obj):
    import yaml
    import jsonpickle
    import json
    s = jsonpickle.encode(obj)
    return yaml.safe_dump(json.loads(s))

def pretty_print(obj):        
    pprint(obj)

