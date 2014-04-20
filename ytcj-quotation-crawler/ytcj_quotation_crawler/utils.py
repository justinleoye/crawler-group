
def ytcj_symbol(s):
    if s=='SH000001':
        s = 'SH1A0001'
    if s.startswith('SH00'):
        s = 'SH1A' + s[4:]
    return s

def normalize_ytcj_symbol(s):
    if s=='SH1A0001':
        s = 'SH000001'
    return s
