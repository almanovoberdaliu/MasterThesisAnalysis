# -*- coding: utf-8 -*-
"""
Klasterizimi sipas pasigurisë konceptuale dhe pengesave  ->  Figura 2.
  Pasiguria = pjesa e 3 lëndëve më të pasigurta ku studenti ka vlerësim <= 3
  Pengesat  = sa nga 3 pengesat më të shpeshta i ka raportuar studenti
"""

from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

import config
from analiza.data_loader import find_col


def get_top_subjects(df, conf_cols, top_n=3):
    """Lëndët me më shumë studentë me vlerësim <= 2."""
    low_pct = (df[conf_cols] <= 2).sum() / len(df)
    return low_pct.sort_values(ascending=False).head(top_n).index.tolist()


def get_top_barriers(barriers_text, top_n=3):
    """Pengesat më të shpeshta (përgjigjet janë të ndara me ';')."""
    split = barriers_text.str.split(";", expand=True).stack().dropna().str.strip()
    return [b for b, _ in Counter(split[split != ""]).most_common(top_n)]


def cluster_uncertainty_barriers(df, conf_cols, subject_map):
    """
    Kthen një fjalor me:
      df            – DataFrame me 'Cluster', 'Perqindja e Ngecjeve', 'Numri i Pengesave'
      summary       – përshkrimi i secilit klaster
      top_subjects  – 3 lëndët më të pasigurta
      top_barriers  – 3 pengesat më të shpeshta
      figure        – Figura 2
    """
    df = df.copy()
    barriers_text = df[find_col(df, config.COL_BARRIERS)].fillna("").astype(str)
    top_subjects = get_top_subjects(df, conf_cols)
    top_barriers = get_top_barriers(barriers_text)

    for b in top_barriers:
        df[b] = barriers_text.apply(lambda x: int(b in x))
    df["Perqindja e Ngecjeve"] = (df[top_subjects] <= 3).sum(axis=1) / len(top_subjects)
    df["Numri i Pengesave"] = df[top_barriers].sum(axis=1)

    subset = df[["Perqindja e Ngecjeve", "Numri i Pengesave"]].dropna()
    scaled = StandardScaler().fit_transform(subset)
    labels = KMeans(n_clusters=config.N_CLUSTERS, random_state=config.RANDOM_STATE,
                    n_init=10).fit_predict(scaled)
    df.loc[subset.index, "Cluster"] = labels
    subset = subset.assign(Cluster=labels)

    return {
        "df": df,
        "summary": describe_clusters(df, top_subjects, top_barriers, subject_map),
        "top_subjects": [subject_map[c] for c in top_subjects],
        "top_barriers": top_barriers,
        "figure": plot_clusters(subset, top_barriers, [subject_map[c] for c in top_subjects]),
    }


def describe_clusters(df, top_subjects, top_barriers, subject_map):
    rows = []
    for k in range(config.N_CLUSTERS):
        part = df[df["Cluster"] == k]
        unc = (part[top_subjects] <= 2).sum() / len(part)
        barriers = part[top_barriers].sum()
        rows.append({
            "Klasteri": k,
            "Studentë": len(part),
            "Pasiguria mesatare": part["Perqindja e Ngecjeve"].mean(),
            "Pengesa mesatare": part["Numri i Pengesave"].mean(),
            "Lënda me më shumë pasiguri": subject_map[unc.sort_values(ascending=False).index[0]],
            "Pengesa kryesore": barriers.idxmax(),
            "Studentë me këtë pengesë": int(barriers.max()),
        })
    return pd.DataFrame(rows)


def plot_clusters(subset, top_barriers, top_subject_labels):
    rng = np.random.default_rng(0)  # "jitter" vetëm për pamjen, nuk ndikon në rezultate
    fig, ax = plt.subplots(figsize=(9, 6))
    sc = ax.scatter(subset["Numri i Pengesave"] + rng.normal(0, 0.1, len(subset)),
                    subset["Perqindja e Ngecjeve"] + rng.normal(0, 0.02, len(subset)),
                    c=subset["Cluster"], cmap="Set2", s=30, alpha=0.6)
    for k in range(config.N_CLUSTERS):
        part = subset[subset["Cluster"] == k]
        ax.text(part["Numri i Pengesave"].mean(), part["Perqindja e Ngecjeve"].mean(),
                f"n={len(part)}", fontsize=10, ha="center")
    ax.set_title("Klasterët sipas Përqindjes së Pasigurisë Konceptuale dhe Pengesave")
    ax.set_xlabel(", ".join(top_barriers))
    ax.set_ylabel(f"Pasiguria ({', '.join(top_subject_labels)})")
    ax.set_xticks([0, 1, 2, 3])
    ticks = np.linspace(0, 1, 6)
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{int(x * 100)}%" for x in ticks])
    fig.colorbar(sc, ax=ax).set_label("Klaster", fontsize=10)
    fig.tight_layout()
    return fig
