# operator.py

import operator
import numpy as np

class Operator:
    revopmap = None # new code added
    def __init__(self, func, expFunc) -> None: # new code added
        self.func = func
        self.expFunc = expFunc
        self.neg = None
        self.imp = None

    def __call__(self, a, b):
        return self.func(a, b)

    def negate(self):
        return Operator(operator.invert(self.func))

    def expected(self, c1, c2):
        return self.expFunc(c1, c2)

    def __repr__(self) -> str:
        return Operator.revopmap[self] # new code added

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Operator):
            return self.func == other.func
        return False

    def __hash__(self):
        fields = (self.func)
        hash_value = hash(fields)
        return hash_value

def eqExp(l, r):
    n = sum(l)**2
    return np.sum(l**2) / n

def neExp(l, r):
    n = sum(l)
    return 1 - np.sum(l**2) / n**2

def geExp(l, r):
    n = sum(l)
    cumFreq = np.cumsum(l)
    return np.sum(l * (cumFreq)) / n**2

def leExp(l, r):
    n = sum(l)
    cumFreq = np.cumsum(l)
    return np.sum(l * (n - cumFreq + l)) / n**2

def gtExp(l, r):
    n = sum(l)
    cumFreq = np.cumsum(l)
    return np.sum(l * (cumFreq - l)) / n**2

def ltExp(l, r):
    n = sum(l)
    cumFreq = np.cumsum(l)
    return np.sum(l * (n - cumFreq)) / n**2


# Operator initializations
# new function added
def initialize_operators():

    eq = Operator(operator.eq, eqExp)
    ne = Operator(operator.ne, neExp)
    ge = Operator(operator.ge, geExp)
    le = Operator(operator.le, leExp)
    gt = Operator(operator.gt, gtExp)
    lt = Operator(operator.lt, ltExp)

    opmap={"==":eq,"<>":ne,">=":ge,"<=":le,">":gt,"<":lt}

    # Reverse mapping (Operator instance -> symbol)
    Operator.revopmap = {v: k for k, v in opmap.items()}  # set class variable


    # Setup negations
    eq.neg = ne
    ne.neg = eq
    gt.neg = le
    le.neg = gt
    lt.neg = ge
    ge.neg = lt

    # Setup implications
    eq.imp = [ge, le, eq]
    ne.imp = [ne]
    gt.imp = [gt, ge, ne]
    lt.imp = [lt, le, ne]
    ge.imp = [ge]
    le.imp = [le]

    # Define mappings
    operatorMap = {
        "EQUAL": eq,
        "UNEQUAL": ne,
        "LESS_EQUAL": le,
        "GREATER_EQUAL": ge,
        "LESS": lt,
        "GREATER": gt
    }

    opmap = {"==": eq, "<>": ne, ">=": ge, "<=": le, ">": gt, "<": lt}


    return operatorMap, opmap, Operator.revopmap


# Predicate
class Predicate:
    def __init__(self,l:str,op:Operator,r:str) -> None:
        self.l=l
        self.r=r
        self.op=op
        self.exp=None
    def __repr__(self) -> str:
        return 't0.'+self.l +' '+self.op.__repr__()+' t1.'+self.r+''
    def __hash__(self):
        fields=(self.l,self.r)
        hash_value = hash(fields)
        return hash_value
    def __eq__(self, other):
        if isinstance(other, Predicate):
            sFields=(self.l,self.op,self.r)
            oFields=(other.l,other.op,other.r)
            return sFields==oFields
        return False
    def impliesPred(self,other):
        #True if predicate being false implies other being false
        return self.l==other.l and self.r==other.r and other.op.neg in self.op.neg.imp


