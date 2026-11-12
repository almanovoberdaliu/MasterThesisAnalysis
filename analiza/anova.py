# -*- coding: utf-8 -*-
"""ANOVA dhe Tukey HSD ndërmjet klasterëve  ->  Seksioni 5.7."""

import pandas as pd
from scipy.stats import f_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def anova_tukey(df, variable):
    """
    Kthen një fjalor me:
      means – numri dhe mesatarja për secilin klaster
      F, p  – rezultati i ANOVA
      tukey – krahasimet në çifte (Tukey HSD)
    """
    data = df.dropna(subset=["Cluster", variable])
    groups = [g[variable].values for _, g in data.groupby("Cluster")]
    f, p = f_oneway(*groups)

    means = data.groupby("Cluster")[variable].agg(["count", "mean"])
    means.index = means.index.astype(int)

    result = pairwise_tukeyhsd(data[variable], data["Cluster"].astype(int))
    table = result.summary().data
    tukey = pd.DataFrame(table[1:], columns=table[0])

    return {"variable": variable, "means": means, "F": f, "p": p,
            "tukey": tukey, "tukey_text": str(result.summary())}
