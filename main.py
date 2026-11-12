# -*- coding: utf-8 -*-
"""
Punim Diplome – Alma Novobërdaliu
Analiza e pasigurisë konceptuale dhe pengesave të studentëve (UBT)

Ekzekutimi nga terminali:   py -3.13 main.py
Ndërfaqja grafike:          py -3.13 -m streamlit run app.py
"""

import sys

import matplotlib

matplotlib.use("Agg")  # figurat ruhen në file, pa hapur dritare
import matplotlib.pyplot as plt

import config
from analiza.data_loader import load_data
from analiza.clustering_profile import cluster_student_profile
from analiza.clustering_barriers import cluster_uncertainty_barriers
from analiza.anova import anova_tukey
from analiza.astar import run_astar


def save(fig, name):
    fig.savefig(config.OUTPUT_DIR / name)
    plt.close(fig)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # shkronjat shqipe në terminalin e Windows
    except AttributeError:
        pass

    config.OUTPUT_DIR.mkdir(exist_ok=True)
    path = sys.argv[1] if len(sys.argv) > 1 else config.DATA_FILE
    try:
        df, conf_cols, subject_map = load_data(path)
    except FileNotFoundError:
        print(f"File-i nuk u gjet: {path}\nVendose Excel-in në dosjen 'data/' me emrin "
              f"'{config.DATA_FILE.name}', ose jepe rrugën: py -3.13 main.py rruga/te/file.xlsx")
        sys.exit(1)
    print(f"U lexuan {len(df)} përgjigje nga '{path}'.")

    # Figura 3 + Figura 4
    prof = cluster_student_profile(df, conf_cols, subject_map)
    print("\n=== Klasterizimi sipas profilit të studentit (Figura 3) ===")
    for r in prof["summary"].itertuples(index=False):
        print(f"Klaster {r[0]} (n = {r[1]}) → Lënda me më shumë pasiguri: {r[2]} ({r[3]} raste me vlerësim ≤ 2)")
    save(prof["figure"], "figura4_pca_klasteret.png")

    # Figura 2
    bar = cluster_uncertainty_barriers(df, conf_cols, subject_map)
    print("\n=== Klasterizimi sipas pasigurisë dhe pengesave (Figura 2) ===")
    for r in bar["summary"].to_dict("records"):
        print(f"Klaster {r['Klasteri']} (n = {r['Studentë']}): pasiguri mesatare = {r['Pasiguria mesatare']:.0%}, "
              f"pengesa mesatare = {r['Pengesa mesatare']:.2f}")
        print(f"   Lënda me më shumë pasiguri: {r['Lënda me më shumë pasiguri']} | "
              f"Pengesa kryesore: {r['Pengesa kryesore']} ({r['Studentë me këtë pengesë']} studentë)")
    save(bar["figure"], "figura2_klasteret_pasiguri_pengesa.png")

    # Seksioni 5.7
    for variable in ["Perqindja e Ngecjeve", "Numri i Pengesave"]:
        res = anova_tukey(bar["df"], variable)
        print(f"\n=== ANOVA: {variable} ===")
        print(res["means"].round(3).to_string())
        print(f"F = {res['F']:.2f}, p = {res['p']:.4g}")
        print(res["tukey_text"])

    # Seksioni 5.4–5.5 + Figura 5
    ast = run_astar(df)
    print("\n=== A*: përgjigjet e studentëve ===")
    for i, counts in enumerate(ast["counts"]):
        print(f"Hapi {i + 1}:")
        for answer, n in counts.items():
            print(f"   {n:4d} × {answer}")
    print(f"\nRruga optimale (A*): {' → '.join(ast['optimal'])} | Kosto: {ast['optimal_cost']}")
    print(f"Rruga mesatare e studentëve: {' → '.join(ast['average'])} | Kosto: {ast['average_cost']}")
    print(f"Diferenca nga optimalja: {ast['difference']:+d}")
    save(ast["figure"], "figura5_rruga_optimale_vs_mesatare.png")

    print(f"\nAnaliza përfundoi. Figurat janë në dosjen: {config.OUTPUT_DIR}")


if __name__ == "__main__":
    main()
