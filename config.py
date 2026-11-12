# -*- coding: utf-8 -*-
"""Konfigurimi i projektit: rrugët e file-ave, parametrat dhe emrat e kolonave."""

from pathlib import Path

# --- Rrugët ---
ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "FormWithSyntheticData.xlsx"
OUTPUT_DIR = ROOT / "output"

# --- Parametrat e K-Means ---
N_CLUSTERS = 3
RANDOM_STATE = 42

# --- Lëndët (në renditjen e kolonave "Sa të sigurt..." në Excel) ---
SUBJECT_NAMES = [
    "Programimi Objekt-Orientuar (OOP)",
    "Strukturat e të Dhënave",
    "Modelimi i Softuerit",
    "Menaxhimi i Projekteve",
    "Bazat e të Dhënave",
    "Zhvillimi Web",
]

# --- Fillimi i emrit të kolonave në Excel ---
COL_GRADE = "Nota Mesatare"
COL_HOURS = "Sa orë në javë"
COL_EXPERIENCE = "A keni përvojë paraprake"
COL_BARRIERS = "Cilat janë pengesat"
COL_CONFIDENCE = "Sa të sigurt"
COL_STEPS = [  # tri pyetjet për A* (Hapi 1, 2, 3)
    "Kur ju jepet një detyrë programimi",
    "Nëse hasni në një problem",
    "Ju jepet detyra të kontrolloni nëse një varg është palindrom",
]

# --- Kostot e veprimeve për A* (supozim i modelit: veprimet më të strukturuara kanë kosto më të ulët) ---
ACTION_COSTS = [
    {  # Hapi 1 – Kur ju jepet një detyrë programimi
        "Hartoj një plan të përgjithshëm": 1,
        "Lexoj kërkesën me kujdes": 2,
        "Kërkoj ndihmë/eksperienca të ngjashme": 3,
        "Filloj menjëherë me kodim": 4,
    },
    {  # Hapi 2 – Nëse hasni në një problem
        "Eksperimentoj me zgjidhje të mundshme": 2,
        "Kthehem dhe filloj nga e para": 3,
        "Kerkoj zgjidhje ne internet": 3,
        "Kërkoj ndihmë nga koleget": 3,
        "E lë problemin për më vonë": 5,
    },
    {  # Hapi 3 – Palindromi
        "Krahasoj direkt karakteret nga të dy anët": 1,
        "Përdor një funksion të ndarë për kontroll": 2,
        "Ndaj vargun në karaktere": 2,
        "Kërkoj një zgjidhje online të ngjashme": 3,
    },
]
