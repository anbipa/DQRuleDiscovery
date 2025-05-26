# dataset.py
import os

import pandas as pd
import numpy as np
import pyarrow.parquet as pq
import warnings

import re
from core.operator_predicate import initialize_operators
from core.operator_predicate import Predicate


class Dataset:
    def __init__(self, file, **args):
        ext = os.path.splitext(file)[-1].lower()
        if ext == ".csv":
            self.columns = pd.read_csv(file, nrows=0).columns
            self.header = [re.match(r'([^\(\)]*)(?:\(| )([^\(\)]*)\)?', col) for col in self.columns]
            self.names = [match[1] for match in self.header]
            typeMap = {'String': str, 'Integer': float, 'Int': float, 'Double': float, 'int': float, 'str': str,
                       'float': float}
            self.types = {col: typeMap[match[2]] for col, match in zip(self.columns, self.header)}

            self.df = pd.read_csv(file, **args, dtype=self.types)
            for i, col in enumerate(self.columns):
                self.df[col] = self.df[col].astype(self.types[col])

        elif ext == ".parquet":
            df = pq.read_table(file).to_pandas().iloc[:2048]

            def is_all_integers(series):
                return all((x == int(x)) for x in series.dropna())

            def infer_series_type(s):
                numeric = pd.to_numeric(s, errors="coerce")
                if numeric.notna().sum() > 0:
                    if is_all_integers(numeric):
                        return numeric.astype("Int64")
                    else:
                        return numeric.astype("Float64")

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    datetime = pd.to_datetime(s, errors="coerce")
                if datetime.notna().sum() > 0 and datetime.notna().sum() >= len(s) * 0.5:
                    return datetime

                return s

            for col in df.columns:
                df[col] = infer_series_type(df[col])

            def map_dtype_to_pytype(dtype):
                if pd.api.types.is_string_dtype(dtype):
                    return str
                elif pd.api.types.is_integer_dtype(dtype):
                    return int
                elif pd.api.types.is_float_dtype(dtype):
                    return float
                elif pd.api.types.is_bool_dtype(dtype):
                    return bool
                elif pd.api.types.is_datetime64_any_dtype(dtype):
                    return pd.Timestamp
                else:
                    return object

            self.df = df
            self.columns = df.columns
            self.header = [[col, str(df[col].dtype)] for col in self.columns]
            self.names = list(self.columns)
            self.types = {col: map_dtype_to_pytype(df[col].dtype) for col in self.columns}

        else:
            raise ValueError(f"Unsupported file extension: {ext}")

        operatorMap, _, _ = initialize_operators()  # Added
        self.eq, self.ne, self.ge, self.le, self.gt, self.lt = operatorMap.values()  # Added

    def randRows(self, n):
        ids = np.random.randint(0, len(self.df), n)
        return self.df.iloc[ids]

    def randFields(self, n):
        return pd.DataFrame(
            {col: self.df[col].iloc[np.random.randint(0, len(self.df), n)].values for col in self.df.columns})

    def buildPLIs(self):
        self.PLI = {col: self.df.groupby(by=col).groups for col in self.df}
        self.PLILen = {col: np.array([len(self.PLI[col][v]) for v in self.PLI[col]]) for col in self.df}
        self.vals = {col: np.array([v for v in self.PLI[col]]) for col in self.df}

    def shuffle(self):
        self.df = self.randFields(len(self.df))

    def buildPreds(self):
        self.preds = []
        self.predMap = {}
        self.colPreds = []
        self.predCols = []

        for col in self.columns:
            ops = [self.eq, self.ne] if self.types[col] == str else [self.eq, self.ne, self.gt, self.ge, self.lt, self.le]
            self.colPreds.append([])
            for op in ops:
                pred = Predicate(col, op, col)
                self.predMap[(col, op, col)] = len(self.preds)
                self.predCols.append(len(self.colPreds))
                self.colPreds[-1].append(len(self.preds))
                self.preds.append(pred)

    def buildEvi(self):
        n = len(self.df)
        m = len(self.preds)
        self.eviSize = n * (n - 1)
        self.evi = [None] * m
        self.predProbs = [None] * m

        for p in range(m):
            pred = self.preds[p]
            col = self.df[pred.l]
            evis = []
            for i in range(n):
                c1 = col.iloc[i]
                c2 = col.iloc[i + 1:n]
                evis.append(pred.op(c1, c2))
                c2 = col.iloc[:i]
                evis.append(pred.op(c1, c2))

            allTPs = np.concatenate(evis)
            self.evi[p] = np.packbits(allTPs, axis=0, bitorder='little')
            self.predProbs[p] = allTPs.sum() / (n * (n - 1)) * 2
        self.sortedPreds = sorted(range(len(self.predProbs)), key=lambda i: self.predProbs[i])
