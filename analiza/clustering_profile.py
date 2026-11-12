# -*- coding: utf-8 -*-
"""
Klasterizimi sipas profilit të studentit  ->  Figura 3 dhe Figura 4.
Veçoritë: nota, orët e studimit, përvoja në programim dhe 6 vlerësimet e sigurisë.
"""

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import config
from analiza.data_loader import find_col


def cluster_student_profile(df, conf_cols, subject_map):
    """
    Kthen një fjalor me:
      profile  – DataFrame me kolonën 'Cluster'
      summary  – tabela e Figurës 3 (klasteri, n, lënda, raste <= 2)
      figure   – Figura 4 (PCA)
    """
    features = [find_col(df, config.COL_GRADE),
                find_col(df, config.COL_HOURS),
                find_col(df, config.COL_EXPERIENCE)] + conf_cols
    data = df[features].dropna()
    scaled = StandardScaler().fit_transform(data)
    clusters = KMeans(n_clusters=config.N_CLUSTERS, random_state=config.RANDOM_STATE,
                      n_init=10).fit_predict(scaled)

    profile = df.loc[data.index].copy()
    profile["Cluster"] = clusters

    return {
        "profile": profile,
        "summary": top_uncertain_subjects(profile, conf_cols, subject_map),
        "figure": plot_pca(scaled, clusters),
    }


def top_uncertain_subjects(profile, conf_cols, subject_map):
    """Figura 3: lënda me më shumë vlerësime <= 2 në secilin klaster."""
    rows = []
    for k in range(config.N_CLUSTERS):
        part = profile[profile["Cluster"] == k]
        low = (part[conf_cols] <= 2).sum()
        col = low.sort_values(ascending=False).index[0]
        rows.append({"Klasteri": k, "Studentë": len(part),
                     "Lënda me më shumë pasiguri": subject_map[col],
                     "Raste me vlerësim ≤ 2": int(low[col])})
    return pd.DataFrame(rows)


def plot_pca(scaled, clusters):
    """Figura 4: klasterët në 2 dimensione përmes PCA."""
    points = PCA(n_components=2).fit_transform(scaled)
    fig, ax = plt.subplots(figsize=(10, 7))
    sc = ax.scatter(points[:, 0], points[:, 1], c=clusters, cmap="viridis", alpha=0.7)
    ax.set_title("Vizualizimi i Klasterëve përmes PCA")
    ax.set_xlabel("PCA Komponenti 1")
    ax.set_ylabel("PCA Komponenti 2")
    fig.colorbar(sc, ax=ax, label="Klaster")
    fig.tight_layout()
    return fig
