# -*- coding: utf-8 -*-
"""
Web interface for the analysis (English).

Run:   py -3.13 -m streamlit run app.py
Opens in the browser at http://localhost:8501
"""

import copy
import io

import matplotlib

matplotlib.use("Agg")
import streamlit as st

import config
from analiza.data_loader import load_data
from analiza.clustering_profile import cluster_student_profile
from analiza.clustering_barriers import cluster_uncertainty_barriers
from analiza.anova import anova_tukey
from analiza.astar import run_astar

st.set_page_config(page_title="Student Analysis – UBT", page_icon="📊", layout="wide")

# -----------------------------------------------------------------------------
# Translations of questionnaire answers (the data itself is in Albanian)
# -----------------------------------------------------------------------------
EN = {
    # subjects
    "Programimi Objekt-Orientuar (OOP)": "Object-Oriented Programming (OOP)",
    "Strukturat e të Dhënave": "Data Structures",
    "Modelimi i Softuerit": "Software Modeling",
    "Menaxhimi i Projekteve": "Project Management",
    "Bazat e të Dhënave": "Databases",
    "Zhvillimi Web": "Web Development",
    # barriers
    "Presioni nga detyrat e tjera": "Pressure from other assignments",
    "Mungesa e motivimit": "Lack of motivation",
    "Mungesa e kohës": "Lack of time",
    "Mungesa e burimeve (p.sh., libra, mjete)": "Lack of resources (e.g., books, tools)",
    "Vështirësi në kuptimin e koncepteve": "Difficulty understanding concepts",
    "Tjetër": "Other",
    # A* actions
    "Hartoj një plan të përgjithshëm": "Draft a general plan",
    "Lexoj kërkesën me kujdes": "Read the requirements carefully",
    "Kërkoj ndihmë/eksperienca të ngjashme": "Seek help / similar experience",
    "Filloj menjëherë me kodim": "Start coding immediately",
    "Eksperimentoj me zgjidhje të mundshme": "Experiment with possible solutions",
    "Kthehem dhe filloj nga e para": "Go back and start over",
    "Kerkoj zgjidhje ne internet": "Search for a solution online",
    "Kërkoj ndihmë nga koleget": "Ask colleagues for help",
    "E lë problemin për më vonë": "Leave the problem for later",
    "Krahasoj direkt karakteret nga të dy anët": "Compare characters from both ends",
    "Përdor një funksion të ndarë për kontroll": "Use a separate check function",
    "Ndaj vargun në karaktere": "Split the string into characters",
    "Kërkoj një zgjidhje online të ngjashme": "Search for a similar solution online",
}
STEP_QUESTIONS = [
    "Step 1 – When given a programming task, what do you do first?",
    "Step 2 – When stuck on a problem, which strategy do you use?",
    "Step 3 – Checking whether a string is a palindrome: first step?",
]


def tr(text):
    return EN.get(text, text)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner="Reading data…")
def load(file_bytes):
    source = io.BytesIO(file_bytes) if file_bytes is not None else config.DATA_FILE
    return load_data(source)


@st.cache_resource(show_spinner="Running clustering…")
def analyse(file_bytes):
    df, conf_cols, subject_map = load(file_bytes)
    prof = cluster_student_profile(df, conf_cols, subject_map)
    bar = cluster_uncertainty_barriers(df, conf_cols, subject_map)
    anovas = [anova_tukey(bar["df"], v) for v in ["Perqindja e Ngecjeve", "Numri i Pengesave"]]

    # English labels on the figures
    ax = bar["figure"].axes[0]
    ax.set_title("Clusters by Conceptual Uncertainty and Learning Barriers")
    ax.set_xlabel("Number of barriers (" + ", ".join(tr(b) for b in bar["top_barriers"]) + ")")
    ax.set_ylabel("Uncertainty (" + ", ".join(tr(s) for s in bar["top_subjects"]) + ")")
    bar["figure"].axes[1].set_ylabel("Cluster")

    ax = prof["figure"].axes[0]
    ax.set_title("Student Clusters – PCA Visualisation")
    ax.set_xlabel("Principal Component 1")
    ax.set_ylabel("Principal Component 2")
    prof["figure"].axes[1].set_ylabel("Cluster")
    return df, prof, bar, anovas


def translate_astar_figure(fig):
    ax = fig.axes[0]
    ax.set_title("Optimal Path vs. Average Student Path")
    ax.set_yticklabels(["Optimal", "Average"])
    ax.set_xticklabels(["Step 1", "Step 2", "Step 3"])
    for t in ax.texts:
        t.set_text(tr(t.get_text()))
    legend = ax.get_legend()
    for t, label in zip(legend.get_texts(), ["Optimal path", "Average path"]):
        t.set_text(label)
    return fig


def fig_download(fig, filename, key):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    st.download_button("⬇️ Download figure (PNG)", buf.getvalue(), file_name=filename,
                       mime="image/png", key=key)


def fmt_p(p):
    return "< 0.001" if p < 0.001 else f"{p:.4f}"


# -----------------------------------------------------------------------------
# Sidebar: data
# -----------------------------------------------------------------------------
st.sidebar.title("📊 Student Analysis")
st.sidebar.caption("Master's Thesis – UBT\n\nAlma Novobërdaliu")
st.sidebar.divider()

uploaded = st.sidebar.file_uploader("Upload the questionnaire Excel file", type=["xlsx"])
if uploaded is not None:
    file_bytes, source_name = uploaded.getvalue(), uploaded.name
elif config.DATA_FILE.exists():
    file_bytes, source_name = None, config.DATA_FILE.name
else:
    st.title("Analysis of Students' Conceptual Uncertainty and Learning Barriers")
    st.info("Upload the questionnaire Excel file in the sidebar, or place it in the `data/` "
            "folder as `FormWithSyntheticData.xlsx`.")
    st.stop()

try:
    df, prof, bar, anovas = analyse(file_bytes)
except Exception as e:
    st.error(f"The file could not be read. Make sure it is the questionnaire export.\n\nError: {e}")
    st.stop()

st.sidebar.success(f"**{source_name}**\n\n{len(df)} responses")
st.sidebar.divider()
st.sidebar.markdown(
    f"**Parameters**\n\n- K-Means: K = {config.N_CLUSTERS}\n"
    f"- random_state = {config.RANDOM_STATE}\n- Scaling: StandardScaler"
)

# -----------------------------------------------------------------------------
# Main page
# -----------------------------------------------------------------------------
st.title("Analysis of Students' Conceptual Uncertainty and Learning Barriers")
st.caption("K-Means · PCA · ANOVA / Tukey HSD · A* search")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Students", len(df))
c2.metric("Clusters", config.N_CLUSTERS)
c3.metric("Most uncertain subject", tr(bar["top_subjects"][0]))
c4.metric("Most common barrier", tr(bar["top_barriers"][0]))

tab_overview, tab_fig2, tab_fig34, tab_anova, tab_astar, tab_data = st.tabs([
    "🏠 Overview", "📍 Uncertainty & Barriers", "🧩 Student Profile (PCA)",
    "📐 ANOVA", "🧭 A* Problem-Solving Path", "🗂️ Data",
])

# --- Overview -------------------------------------------------------------------
with tab_overview:
    st.subheader("Key findings")
    for r in bar["summary"].to_dict("records"):
        st.markdown(
            f"**Cluster {r['Klasteri']}** ({r['Studentë']} students): average uncertainty "
            f"**{r['Pasiguria mesatare']:.0%}**, on average **{r['Pengesa mesatare']:.2f}** barriers. "
            f"Most uncertain subject: *{tr(r['Lënda me më shumë pasiguri'])}*; "
            f"main barrier: *{tr(r['Pengesa kryesore'])}*."
        )
    st.divider()
    left, right = st.columns(2)
    with left:
        st.markdown("**Top 3 subjects by uncertainty**")
        for i, name in enumerate(bar["top_subjects"], 1):
            st.markdown(f"{i}. {tr(name)}")
    with right:
        st.markdown("**Top 3 reported barriers**")
        for i, name in enumerate(bar["top_barriers"], 1):
            st.markdown(f"{i}. {tr(name)}")

# --- Figure 2 -------------------------------------------------------------------
with tab_fig2:
    st.subheader("Clusters by conceptual uncertainty and barriers (Figure 2)")
    st.caption("Uncertainty = share of the 3 most uncertain subjects rated ≤ 3 by the student. "
               "Barriers = how many of the 3 most common barriers the student reported.")
    st.pyplot(bar["figure"])
    fig_download(bar["figure"], "figure2_uncertainty_barriers.png", "dl2")

    table = bar["summary"].rename(columns={
        "Klasteri": "Cluster", "Studentë": "Students",
        "Pasiguria mesatare": "Avg. uncertainty", "Pengesa mesatare": "Avg. barriers",
        "Lënda me më shumë pasiguri": "Most uncertain subject",
        "Pengesa kryesore": "Main barrier", "Studentë me këtë pengesë": "Students with this barrier",
    })
    table["Avg. uncertainty"] = table["Avg. uncertainty"].map("{:.0%}".format)
    table["Avg. barriers"] = table["Avg. barriers"].map("{:.2f}".format)
    table["Most uncertain subject"] = table["Most uncertain subject"].map(tr)
    table["Main barrier"] = table["Main barrier"].map(tr)
    st.dataframe(table, hide_index=True, width="stretch")

# --- Figures 3 + 4 --------------------------------------------------------------
with tab_fig34:
    st.subheader("Clustering by student profile (Figures 3 and 4)")
    st.caption("Features: average grade, weekly study hours, prior programming experience and "
               "self-rated confidence in 6 subjects. This is a different clustering from Figure 2.")
    st.markdown("**Subject with the most low ratings (1 or 2) in each cluster**")
    t = prof["summary"].rename(columns={
        "Klasteri": "Cluster", "Studentë": "Students",
        "Lënda me më shumë pasiguri": "Most uncertain subject",
        "Raste me vlerësim ≤ 2": "Ratings ≤ 2",
    })
    t["Most uncertain subject"] = t["Most uncertain subject"].map(tr)
    st.dataframe(t, hide_index=True, width="stretch")
    st.pyplot(prof["figure"])
    fig_download(prof["figure"], "figure4_pca_clusters.png", "dl4")

# --- ANOVA ----------------------------------------------------------------------
with tab_anova:
    st.subheader("Comparison between clusters (Section 5.7)")
    st.caption("One-way ANOVA and Tukey HSD post-hoc test on the clusters of Figure 2.")
    titles = {"Perqindja e Ngecjeve": "Conceptual uncertainty", "Numri i Pengesave": "Number of barriers"}
    for res in anovas:
        st.markdown(f"#### {titles[res['variable']]}")
        a, b = st.columns(2)
        a.metric("F", f"{res['F']:.2f}")
        b.metric("p-value", fmt_p(res["p"]))
        means = res["means"].rename(columns={"count": "Students", "mean": "Mean"})
        means.index.name = "Cluster"
        left, right = st.columns([1, 2])
        left.dataframe(means.round(3), width="stretch")
        right.dataframe(res["tukey"], hide_index=True, width="stretch")
    st.info("The clusters were built from these two variables, so the differences between them "
            "are almost always significant. This should be noted as a limitation.")

# --- A* -------------------------------------------------------------------------
with tab_astar:
    st.subheader("Optimal path vs. average student path (Sections 5.4–5.5)")
    st.caption("The graph has 3 steps (questions 17, 18, 19). A* finds the lowest-cost path; the "
               "average path is the most frequent answer at each step. Action costs can be edited below.")

    with st.expander("⚙️ Action costs", expanded=False):
        costs = copy.deepcopy(config.ACTION_COSTS)
        for i, col in enumerate(st.columns(3)):
            with col:
                st.markdown(f"**Step {i + 1}**")
                for action in costs[i]:
                    costs[i][action] = st.number_input(tr(action), min_value=0, max_value=20,
                                                       value=int(costs[i][action]), step=1,
                                                       key=f"cost_{i}_{action}")

    ast = run_astar(df, costs)

    a, b, c = st.columns(3)
    a.metric("Optimal path cost", ast["optimal_cost"])
    b.metric("Average path cost", ast["average_cost"])
    c.metric("Difference", f"{ast['difference']:+d}")

    st.markdown("**Optimal path (A\\*):** " + " → ".join(tr(x) for x in ast["optimal"]))
    st.markdown("**Average student path:** " + " → ".join(tr(x) for x in ast["average"]))
    fig = translate_astar_figure(ast["figure"])
    st.pyplot(fig)
    fig_download(fig, "figure5_optimal_vs_average_path.png", "dl5")

    st.markdown("**Student answers per step**")
    for i, (col, counts) in enumerate(zip(st.columns(3), ast["counts"])):
        with col:
            st.caption(STEP_QUESTIONS[i])
            t = counts.rename_axis("Answer").reset_index(name="Students")
            t["Answer"] = t["Answer"].map(tr)
            st.dataframe(t, hide_index=True, width="stretch")

# --- Data -----------------------------------------------------------------------
with tab_data:
    st.subheader("Data with cluster labels")
    st.caption("Questionnaire columns are shown in their original language (Albanian).")
    out = bar["df"].copy()
    out = out.rename(columns={"Perqindja e Ngecjeve": "Uncertainty share",
                              "Numri i Pengesave": "Number of barriers"})
    out["Cluster (Figure 2)"] = out.pop("Cluster").astype("Int64")
    out["Cluster (Figures 3/4)"] = prof["profile"]["Cluster"]
    st.dataframe(out, width="stretch", height=450)
    st.download_button("⬇️ Download as CSV", out.to_csv(index=False).encode("utf-8-sig"),
                       file_name="clustered_results.csv", mime="text/csv")
