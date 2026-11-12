# Analysis of Students' Conceptual Uncertainty and Learning Barriers

Source code for the Master's thesis at UBT – Alma Novobërdaliu.

The project clusters students with K-Means based on their self-reported conceptual
uncertainty and learning barriers, visualises the clusters with PCA, compares them with
ANOVA / Tukey HSD, and uses the A* search algorithm to compare the optimal
problem-solving path with the path most students actually follow.

## Structure

```
AnalizaStudentet/
├── app.py                       # web interface (Streamlit)
├── main.py                      # runs the full analysis from the terminal
├── config.py                    # paths, parameters, column names, A* action costs
├── requirements.txt             # dependencies
├── data/
│   └── FormWithSyntheticData.xlsx   (not included, see "Data")
├── output/                      # figures saved by main.py (created automatically)
└── analiza/
    ├── data_loader.py           # reads the Excel file and prepares the data
    ├── clustering_profile.py    # K-Means on student profile -> Figure 3, Figure 4 (PCA)
    ├── clustering_barriers.py   # K-Means on uncertainty and barriers -> Figure 2
    ├── anova.py                 # ANOVA + Tukey HSD -> Section 5.7
    └── astar.py                 # A* optimal vs. average path -> Sections 5.4–5.5, Figure 5
```

## Installation

```
py -3.13 -m pip install -r requirements.txt
```

## Usage

### Web interface

```
py -3.13 -m streamlit run app.py
```

The app opens in the browser at http://localhost:8501. Upload the questionnaire Excel
file in the sidebar (or place it in `data/`). The interface has tabs for the summary,
Figure 2, Figures 3–4 (PCA), ANOVA, A* (with editable action costs) and the data table.
Every figure and the clustered data can be downloaded.

### Terminal

```
py -3.13 main.py
```

Numerical results are printed to the terminal; figures are saved to `output/`:

| File                                     | In the thesis |
|------------------------------------------|---------------|
| `figura2_klasteret_pasiguri_pengesa.png` | Figure 2      |
| (terminal output)                        | Figure 3      |
| `figura4_pca_klasteret.png`              | Figure 4      |
| `figura5_rruga_optimale_vs_mesatare.png` | Figure 5      |

K-Means uses `random_state=42`, so the results are identical on every run.

## Data

The dataset is not included in this repository to protect participants' privacy.
To run the analysis, place `FormWithSyntheticData.xlsx` in the `data/` folder or upload it
in the web interface.
