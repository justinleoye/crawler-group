
def flatten(s):
    r = []
    for x in s:
        r += list(x)
    return r 
        

def list_abbr(a, firstn=10, lastn=10, seperator=None):
    if len(a)<=firstn+lastn:
        return a
    else:
        a1 = a[:firstn]
        a2 = a[-lastn:]
        if seperator is not None:
            return  a1 + [seperator] + a2
        else:
            return a1 + a2
