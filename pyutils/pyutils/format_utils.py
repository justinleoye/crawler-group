
def get_number(s):
    if isinstance(s, (float, int)):
        return s
    elif isinstance(s, (str, unicode)):
        m = 1
        s = s.strip()
        try:
            if s[-1]==u'亿':
                m = 100000000
                s = s[:-1]
            elif s[-1]==u'万':
                s = s[:-1]
                m = 10000
            return float(s)*m
        except:
            return None
    else:
        return None


