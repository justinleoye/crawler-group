import random

def iter_sample(iterable, samplesize):
    results = []
    iterator = iter(iterable)
    # Fill in the first samplesize elements:
    try:
        for i in xrange(samplesize):
            results.append(iterator.next())
    except StopIteration:
        #raise ValueError("Sample larger than population.")
        return results

    random.shuffle(results)
    n = samplesize
    for v in iterator:
        r = random.randint(0, n) #0<=r<=n
        # at a decreasing rate, replace random items
        if r < samplesize:
            results[r] = v  
        n += 1
    return results
