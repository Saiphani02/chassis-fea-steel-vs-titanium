"""Draws the comparison chart in images/comparison.png from results/summary.json."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

here = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(here, "..", "..", "results", "summary.json")))
labels = ["Steel\n5 mm", "Ti-6Al-4V\n2 mm", "Ti-6Al-4V\n3 mm", "Ti-6Al-4V\n8.8 mm"]
colors = ["#5b6770", "#c8782a", "#e0a458", "#8f4f12"]
fig, ax = plt.subplots(1, 3, figsize=(13, 4.2))
panels = [("mass_kg", "Frame mass (kg)", None),
          ("bump_defl_mm", "Sag under 2.5 g bump (mm)", None),
          ("diag_defl_mm", "Free-corner drop, diagonal lift (mm)", None)]
for a, (key, title, _) in zip(ax, panels):
    vals = [r[key] for r in rows]
    bars = a.bar(labels, vals, color=colors, width=0.62)
    a.set_title(title, fontsize=11, loc="left")
    a.spines[["top", "right"]].set_visible(False)
    a.tick_params(axis="x", labelsize=9)
    for b, v in zip(bars, vals):
        a.text(b.get_x() + b.get_width() / 2, v, ("%.0f" if v >= 20 else "%.1f") % v, ha="center", va="bottom", fontsize=9)
fig.suptitle("Ladder frame: steel baseline vs titanium at three wall thicknesses (Ansys Mechanical, shell model)", fontsize=12, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(os.path.join(here, "..", "..", "images", "comparison.png"), dpi=150)
