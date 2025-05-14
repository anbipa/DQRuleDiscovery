import re

class DenialConstraint:
    def __init__(self, preds) -> None:
        self.preds = preds

    def __sub__(self, other):
        return DenialConstraint(self.preds - other.preds)

    def __le__(self, other):
        other: DenialConstraint = other
        return all([any([p == pp for pp in other.preds]) for p in self.preds])

    def __eq__(self, value: object) -> bool:
        return self <= value and value <= self

    def __repr__(self) -> str:
        return "¬(" + " ^ ".join([pred.__repr__() for pred in self.preds]) + ")"


class DenialConstraintSet:
    def __init__(self, path, dataset, dss, algorithm, opmap) -> None:  # Added opmap
        self.predMap = {}
        self.preds = []
        self.dss = dss

        def getPred(c1, op, c2):
            op = opmap[op]
            return dss.predMap[(c1, op, c2)]

        self.DCs = []

        with open(path) as f:
            for line in f:
                line = line.strip()[2:-1]  # strip !(...)
                preds = line.split('^')
                regex = r't0\.' + dataset + '\.csv\.([^=><]*)(==|<>|>=|<=|>|<)t1\.' + dataset + '\.csv\.([^=><]*)'
                if algorithm in ['ADCMiner', 'FastADC', 'ours']:
                    regex = r't0\.([^=><]*) (==|<>|>=|<=|>|<) t1\.([^=><]*)'
                preds = [getPred(*re.match(regex, pred.strip()).groups()) for pred in preds]
                self.DCs.append(preds)

    def buildGraph(self):
        self.root = [{}, None]
        for dc in self.DCs:
            node = self.root
            for pred in sorted(dc):
                if pred not in node[0]:
                    node[0][pred] = [{}, None]
                node = node[0][pred]
            node[1] = dc

    def getReduced(self):

        notImplied = [True] * len(self.DCs)

        def impliesDC(dc1, dc2):
            return all(
                [any([self.dss.preds[pred].impliesPred(self.dss.preds[otherpred]) for otherpred in dc2]) for pred in
                 dc1])

        for i, dc1 in enumerate(self.DCs):
            for j, dc2 in enumerate(self.DCs):
                if impliesDC(dc1, dc2):
                    if impliesDC(dc2, dc1):
                        notImplied[j] = notImplied[j] and j <= i
                    else:
                        notImplied[j] = False
        return [dc for i, dc in enumerate(self.DCs) if notImplied[i]]