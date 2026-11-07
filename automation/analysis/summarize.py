import json, os, subprocess
os.environ["NODES"] = "nodes_e15.txt"
import importlib.util
spec = importlib.util.spec_from_file_location("ff", "farfield.py")
rows = []
Sy = {"Steel S355": 355.0, "Ti-6Al-4V": 880.0}
for tag in ["steel_t5", "ti_t2", "ti_t3", "ti_t88"]:
    d = json.load(open("result_%s.json" % tag))
    row = dict(tag=tag, material=d["material"], t_rail=d["t_rail"], t_cross=d["t_cross"], mass_kg=round(d["mass_kg"], 1),
               buckling_factor=round(d.get("buckling_load_multiplier_mode1", float("nan")), 2))
    for case, key in (("Bump 2.5g", "bump"), ("Diagonal lift 1g", "diag")):
        r = d[case]
        row[key + "_defl_mm"] = round(-r["Vertical deflection"]["min"], 2)
        row[key + "_peak_MPa"] = round(r["Von Mises"]["max"], 1)
        out = subprocess.run(["python3", "farfield.py", "vm_%s_%s.txt" % (tag, case.replace(" ", "_").replace(".", ""))],
                             capture_output=True, text=True, env=os.environ).stdout.splitlines()[0]
        ff = float(out.split("far-field max ")[1].split(" ")[0])
        row[key + "_farfield_MPa"] = ff
        row[key + "_SF"] = round(Sy[d["material"]] / ff, 2)
    rows.append(row)
json.dump(rows, open("summary.json", "w"), indent=1)
for r in rows: print(r)
