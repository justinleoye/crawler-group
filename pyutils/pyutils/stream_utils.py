from itertools import imap

from pyutils.type_utils import get_list
from pyutils.iter_utils import imerge, igroupby

def merge_streams(stream_dict, sort_key, is_multi=True):
    sort_key = get_list(sort_key)

    if is_multi in [True, False]:
        is_multi = {k: is_multi for k in stream_dict}

    def map_for_merge(qid):
        def f(r):
            return [r[k] for k in sort_key] + [qid, r]
        return f

    stream_list = (imap(map_for_merge(k), s) for k,s in stream_dict.iteritems())
    merged_stream = imerge(*stream_list)

    nk = len(sort_key)
    grouped_stream = igroupby(merged_stream, lambda r: r[:nk])

    def make_ret_rec():
        d = {}
        for key in stream_dict:
            if is_multi.get(key):
                d[key] = []
            else:
                d[key] = None
        return d

    for t, g in grouped_stream:
        d = make_ret_rec()
        for time,key,rec in g:
            if is_multi.get(key):
                d[key].append(rec)
            else:
                d[key] = rec
        for i in range(nk):
            d[sort_key[i]] = t[i]
        yield d

