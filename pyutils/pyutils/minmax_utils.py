
def min_with_none(a, b):
    if a is None:
        return b
    elif b is None:
        return a
    else:
        return min(a,b)

def max_with_none(a, b):
    #None is smallest value
    return max(a,b)

