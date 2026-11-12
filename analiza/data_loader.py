# -*- coding: utf-8 -*-
"""Leximi i Excel-it dhe kthimi i përgjigjeve tekstuale në vlera numerike."""

import pandas as pd

import config


def find_col(df, prefix):
    """Kthen kolonën e parë që fillon me tekstin e dhënë."""
    return next(c for c in df.columns if c.startswith(prefix))


def convert_grade(grade):
    """'7.00 - 8.49' -> 7.745 (mesi i intervalit)."""
    try:
        if isinstance(grade, str):
            if "-" in grade:
                low, high = map(float, grade.split(" - "))
                return (low + high) / 2
            return float(grade)
        return float(grade) if pd.notna(grade) else 0
    except (ValueError, TypeError):
        return 0


def convert_study_hours(hours):
    """Intervali i orëve të studimit -> numër orësh."""
    try:
        if isinstance(hours, str):
            if "Më pak se 5" in hours:
                return 3
            if "5-8" in hours:
                return 6.5
            if "8 - 12" in hours:
                return 10
            if "Më shumë se 12" in hours:
                return 15
            return float(hours)
        return float(hours) if pd.notna(hours) else 0
    except (ValueError, TypeError):
        return 0


def convert_experience(exp):
    """Përvoja në programim -> 0 (asnjë) deri 3 (e avancuar)."""
    if not isinstance(exp, str):
        return 0
    exp = exp.lower()
    if "asnjë" in exp:
        return 0
    if "bazë" in exp or "basic" in exp:
        return 1
    if "mesatare" in exp or "intermediate" in exp:
        return 2
    if "avancuar" in exp or "advanced" in exp:
        return 3
    return 0


def load_data(source=config.DATA_FILE):
    """
    Lexon Excel-in (rrugë file-i ose file i ngarkuar) dhe kthen:
    (df, kolonat e sigurisë, {kolona: emri i lëndës})
    """
    df = pd.read_excel(source)
    df.columns = [str(c).replace("\n", "").replace("\xa0", " ").strip() for c in df.columns]

    df[find_col(df, config.COL_GRADE)] = df[find_col(df, config.COL_GRADE)].apply(convert_grade)
    df[find_col(df, config.COL_HOURS)] = df[find_col(df, config.COL_HOURS)].apply(convert_study_hours)
    df[find_col(df, config.COL_EXPERIENCE)] = df[find_col(df, config.COL_EXPERIENCE)].apply(convert_experience)

    conf_cols = [c for c in df.columns if c.startswith(config.COL_CONFIDENCE)]
    for c in conf_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
        df[c] = df[c].fillna(df[c].mean())

    subject_map = dict(zip(conf_cols, config.SUBJECT_NAMES))
    return df, conf_cols, subject_map
