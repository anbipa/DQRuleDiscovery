from core.dataset import Dataset
from core.utils import powerset, y1, y2
import numpy as np
from core.denialconstraints import DenialConstraint

def discover_unique_constraints(dataset_path, row_count=2048, depth=4):
    # Load dataset
    ds = Dataset(dataset_path, nrows=row_count, encoding='unicode_escape')

    # Build index structures
    ds.buildPLIs()
    ds.buildPreds()
    ds.buildEvi()

    counts = {}

    def count_pred_sets(preds, cols, x):
        counts[preds] = np.bitwise_count(x).sum()
        if len(preds) >= depth:
            return
        for pred in ds.sortedPreds:
            ncol = ds.predCols[pred]
            if ncol in cols:
                continue
            npreds = preds | {pred}
            ncols = cols | {ncol}
            if npreds in counts:
                continue
            newx = np.bitwise_and(x, ds.evi[pred])
            count_pred_sets(npreds, ncols, newx)

    count_pred_sets(frozenset(), frozenset(), np.full((ds.eviSize // 8,), 255, dtype=np.uint8))

    y1_function = y1()
    y2_function = y2()

    visited = set()
    DCResults = []

    def search(preds, cols):
        if preds in visited:
            return
        visited.add(preds)
        if len(preds) >= depth:
            return
        for pred in ds.sortedPreds:
            ncol = ds.predCols[pred]
            if ncol in cols:
                continue
            npreds = preds | {pred}
            ncols = cols | {ncol}
            a1 = int(counts[npreds])
            b1 = int(counts[preds]) - a1
            valid = True
            for subPreds in powerset(preds):
                subPreds = frozenset(subPreds)
                npreds2 = subPreds | {pred}
                a2 = int(counts[npreds2])
                b2 = int(counts[subPreds]) - a2
                u = y1_function(a1 + 1) - y1_function(b1 + 1) - y1_function(a2 + 1) + y1_function(b2 + 1)
                s = np.sqrt(y2_function(a1 + 1) + y2_function(b1 + 1) + y2_function(a2 + 1) + y2_function(b2 + 1))
                if u + 2 * s > 0:
                    valid = False
                    break
            if valid:
                if a1 == 0:
                    DCResults.append((preds, pred))
                else:
                    search(npreds, ncols)

    search(frozenset(), frozenset())

    def getPred(i, ds):
        return ds.preds[i]

    dcs = set()
    dcs_out = []

    for dc in [DenialConstraint([getPred(p, ds) for p in preds] + [getPred(pred, ds)]) for preds, pred in DCResults]:
        if all(pred.op.__repr__() == "==" for pred in dc.preds):
            s = frozenset(dc.preds)
            if s not in dcs:
                dcs.add(s)
                dcs_out.append(dc.__repr__())

    return dcs_out
