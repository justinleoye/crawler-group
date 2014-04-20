import json

def convert_str_to_type(v, t):
    if t=='integer':
        return int(v)
    elif t=='number':
        return float(v)
    elif t=='boolean':
        v = v.lower()
        return v and v!='0' and v!='false' and v!='off' and v!='no'
    elif t=='json':
        return json.loads(v)
    else:
        raise Exception("unknown type: %s" % t)

