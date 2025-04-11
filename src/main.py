# main.py
from dataset import Dataset
from utils import powerset, y1, y2
import numpy as np
from denialconstraints import DenialConstraint

# Dataset initialization
dataset = "input"
rowCount = 1 << 11

# Load dataset
ds = Dataset("../data/" + dataset + ".csv", nrows=rowCount, encoding='unicode_escape')

# Build Position List Indexes (PLIs)
ds.buildPLIs()

# Build the predicates
ds.buildPreds()

# Build the evidence set
ds.buildEvi()

#Max size of predicate sets to search for
depth=4
DCCounts={}
counts={}

#Recursive function that performs a DFS search across the space of predicate sets up to length 4.
def search(preds,cols,x):
    #For every visited set of predicates, compute the proportion of tuple pairs it satisfies and store it.
    counts[preds]=np.bitwise_count(x).sum() # bitwise_count before
    #Stop the search if we are at max depth
    if len(preds)>=depth:
            return
    #Otherwise, continue the DFS by exploring all predicate sets reachable from the current one by adding a new predicate.
    for pred in ds.sortedPreds:
            #We do not attempt to add predicates over the same column. This generates trivial DCs. Ex: State=State and State !=State.
            ncol=ds.predCols[pred]
            if ncol in cols:
                continue
            #This is a predicate set we want to visit. Explore it only if it has not been visited already.
            npreds=preds|{pred}
            ncols=cols|{ncol}
            if npreds in counts:
                continue
            #This is an unvisited predicate set we want to visit. Filter the tuple pairs so as to keep those that satisfy the new set of predicates.
            newx=np.bitwise_and(x,ds.evi[pred])
            #Recursive call
            search(npreds,ncols,newx)

#Begin search:
search(frozenset()  #Begin with an empty set of predicates
       ,frozenset(),#Begin with no columns having predicates on the current set, as it is empty
       np.full((ds.eviSize//8,),255,dtype=np.uint8))#Begin with all tuple pairs fulfilling the predicate set, as there is no predicate to not fulfill. This gets filtered as predicates are added during the DFS.

DCCounts=counts

DCResults = {}

counts = DCCounts
DCResult = []
visited = set()


# Recursive function like before, to explore in DFS the space of predicate sets up to a given depth.
def search(preds, cols):
    # Every candidate needs to be evaluated only once
    if preds in visited:
        return
    visited.add(preds)

    # Like before, stop at maximum depth
    if len(preds) >= depth:
        return

    # If we are evaluating {A,B,C}, we iterate through p(A|BC),p(B|AC),p(C|AB).
    # For each of them, we compare it with the respective subsets:
    # p(A|BC)< p(A|B), p(A|C), p(A)
    # p(B|AC)< p(B|A), p(B|C), p(B)
    # p(C|AB)< p(C|A), p(C|B), p(C)

    # A DC is only accepted when the inequalities are statistically significant
    # indicating there is some relationship among this particular set of predicates
    # that is not captured by any of its subsets
    for pred in ds.sortedPreds:
        # As before, we do not add predicates over already used columns to avoid trivial DCs.
        ncol = ds.predCols[pred]
        if ncol in cols:
            continue

        # Determine if the DC is valid
        npreds = preds | {pred}
        ncols = cols | {ncol}

        # a and b are number of successes and failures of a Bernouilli radnom variable
        # In our case, the number of tuple pairs that fulfill pred when the others in preds are true.
        # Ex: a1=|ABC|/|BC|, b1=|(!A)BC|/|BC|
        a1 = int(counts[npreds])
        b1 = int(counts[preds]) - a1

        # Assume validity until some conditional of a subset is not significantly different from the current conditional
        valid = True
        for subPreds in powerset(preds):
            # For every subset of preds, compare the conditionals
            # Ex: compare p(A|BC) with p(A|B)
            subPreds = frozenset(subPreds)
            npreds2 = subPreds | {pred}

            # Ex: a1=|AB|/|B|, b1=|(!A)B|/|B|
            a2 = int(counts[npreds2])
            b2 = int(counts[subPreds]) - a2

            # If the population probability of p(A|BC) is u1 and the one of p(A|B) is u2,
            # given our information a1,a2,b1,b2, we know the distribution of ln((a1*b2)/(b1*a2)) has mean:
            u = y1(a1 + 1) - y1(b1 + 1) - y1(a2 + 1) + y1(b2 + 1)

            # and standard deviation
            s = np.sqrt(y2(a1 + 1) + y2(b1 + 1) + y2(a2 + 1) + y2(b2 + 1))

            # If the mean is more than 2 standard deviations from 0, it statistically significant enough for us to claim
            # the conditional p(A|BC) is smaller than p(A|B), and therefore there is some relationship
            # Otherwise, there is not enough evidence and this difference in distribution could be due to randomness.
            if u + 2 * s > 0:
                valid = False
                break
        if valid:
            # If is valid, there is some significant relationship between the predicates
            # However, we only accept a DC when it is a set of exclusive predicates.
            # This means p(A|BC) must be 0.
            # Optionally, approximate DCs may be discovered by changing this condition to:
            # a1/(a1+b1)<0.01
            # where 0.01 is a 1% approximation factor.
            if a1 == 0:
                DCResult.append((preds, pred))
            else:
                search(npreds, ncols)

y1=y1()
y2=y2()

# Begin search on the empty set of predicates
search(frozenset(), frozenset())

DCResults = DCResult


# Export the results
def getPred(i,ds):
    return (ds.preds[i])


dcs=set({})

with open(f"../outputs/result_{dataset}","w") as f:
    for dc in [ DenialConstraint([ getPred(p,ds) for p in preds]+[getPred(pred,ds)]) for preds,pred in DCResults]:
        s=frozenset(dc.preds)
        if s not in dcs:
            dcs.add(s)
            f.write(dc.__repr__()+"\n")
