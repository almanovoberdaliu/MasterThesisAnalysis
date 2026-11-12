
import heapq

import matplotlib.pyplot as plt

import config
from analiza.data_loader import find_col


def heuristic(layer, costs):

    return sum(min(c.values()) for c in costs[layer:])


def find_optimal_path(costs):
    counter = 0  # për barazimet në heap
    open_list = [(heuristic(0, costs), counter, 0, 0, [])]  # (f, nr, g, shtresa, rruga)
    closed = set()
    while open_list:
        _, _, g, layer, path = heapq.heappop(open_list)
        if layer == len(costs):
            return path, g
        node = (layer, path[-1] if path else None)
        if node in closed:
            continue
        closed.add(node)
        for action, cost in costs[layer].items():
            counter += 1
            new_g = g + cost
            heapq.heappush(open_list, (new_g + heuristic(layer + 1, costs), counter, new_g, layer + 1, path + [action]))
    return [], None


def answer_counts(df):
    """Sa herë është zgjedhur secila përgjigje në secilin hap."""
    return [df[find_col(df, prefix)].dropna().astype(str).str.strip().value_counts()
            for prefix in config.COL_STEPS]


def average_student_path(counts, costs):
    """Përgjigjja më e shpeshtë për secilin hap (në barazim: ajo me kosto më të ulët)."""
    return [max(c.items(), key=lambda kv: (kv[1], -costs[i].get(kv[0], 99)))[0]
            for i, c in enumerate(counts)]


def path_cost(path, costs):
    return sum(costs[i].get(a, 0) for i, a in enumerate(path))


def run_astar(df, costs=None):
  
    costs = costs or config.ACTION_COSTS
    optimal, opt_cost = find_optimal_path(costs)
    counts = answer_counts(df)
    average = average_student_path(counts, costs)
    avg_cost = path_cost(average, costs)

    return {
        "optimal": optimal, "optimal_cost": opt_cost,
        "average": average, "average_cost": avg_cost,
        "difference": avg_cost - opt_cost,
        "counts": counts,
        "figure": plot_paths(optimal, average),
    }


def plot_paths(optimal, average):
    fig, ax = plt.subplots(figsize=(12, 4))
    for y, (label, path, color) in zip([1, 0], [("Rruga optimale", optimal, "tab:green"),
                                                ("Rruga mesatare", average, "tab:orange")]):
        ax.plot(range(len(path)), [y] * len(path), "-o", color=color, label=label, markersize=10)
        for i, action in enumerate(path):
            ax.annotate(action, (i, y), textcoords="offset points", xytext=(0, 12), ha="center", fontsize=8)
    ax.set_yticks([1, 0])
    ax.set_yticklabels(["Optimale", "Mesatare"])
    ax.set_xticks(range(3))
    ax.set_xticklabels(["Hapi 1", "Hapi 2", "Hapi 3"])
    ax.set_ylim(-0.6, 1.6)
    ax.set_xlim(-0.6, 2.6)
    ax.legend(loc="lower right")
    ax.set_title("Krahasimi ndërmjet rrugës optimale dhe rrugës mesatare")
    fig.tight_layout()
    return fig
