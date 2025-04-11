# utils.py

import itertools
import numpy as np

def powerset(iterable):
    """Generate the powerset of a given iterable."""
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)))

def y1():
    """Memoization for the digamma function."""
    mem = [-0.5772156649]
    def f(n):
        while len(mem) < n:
            mem.append(mem[-1] + 1 / len(mem))
        return mem[n-1]
    return f

def y2():
    """Memoization for the trigamma function."""
    mem = [np.pi**2 / 6]
    def f(n):
        while len(mem) < n:
            mem.append(mem[-1] - 1 / len(mem)**2)
        return mem[n-1]
    return f
