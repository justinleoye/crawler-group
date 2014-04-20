from .type_utils import *

def get_schema(schema):
    if schema is None:
        return None
    if is_str(schema):
        return split_schema(schema)
    else:
        return list(schema)

def get_fields(fields):
    return get_schema(fields)

def get_schema_str(schema):
    if is_str(schema):
        return schema
    else:
        return join_schema(schema)

def split_schema(schema_str):
    schema = map(lambda x: x.strip(), schema_str.split(','))
    return schema

def join_schema(schema):
    return ','.join(schema)
    
def get_schema_from_comment(comment):
    schema = []
    for s in comment.split('\n'):
        t = s.strip()
        if not t:
            continue
        schema.append(t.split()[0])
    return schema

