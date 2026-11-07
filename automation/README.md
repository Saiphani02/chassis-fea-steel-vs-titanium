# Automation scripts

The four frame designs in this study share one model and differ only in material and wall thickness.
These scripts rerun that model for each design and post-process the results.

| Folder / file | What it does |
| --- | --- |
| `ansys/01_import.py` | Imports the midsurface STEP and the two materials (`materials.xml`) into Mechanical |
| `ansys/02_mesh_connections.py` | Joins the surface bodies along shared edges (welded joints) |
| `ansys/03_model.py` | Named selections, supports, the two load cases and result objects |
| `ansys/04_solve_variant.py` | Sets material and thickness from `variant.json`, meshes, solves, exports results |
| `ansys/05_export_nodes.py` | Node coordinates for the far-field stress filter |
| `ansys/mech_run.py` | Sends a script to a running Mechanical session through PyMechanical |
| `analysis/handcalc.py` | Beam-theory checks (bending stress and a 1D beam FE model for deflection) |
| `analysis/farfield.py` | Separates joint hot spots from far-field stress |
| `analysis/summarize.py` | Builds `results/summary.json` |
| `analysis/make_charts.py` | Draws `images/comparison.png` |
| `freecad_build_chassis.py` | Builds the midsurface geometry used for the shell model |

To rerun: start Mechanical with gRPC enabled
(`AnsysWBU.exe -DSApplet -AppModeMech -grpc 10000 --transport-mode wnua`), run the `ansys/` scripts in
order with `python mech_run.py <script>`, then run `04_solve_variant.py` once per `variant.json`.

```
pip install -r requirements.txt
python analysis/handcalc.py
```
