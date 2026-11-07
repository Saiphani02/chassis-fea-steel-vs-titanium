# Ladder-frame chassis FEA: steel vs titanium

How much weight do you actually save by building a vehicle ladder frame in Ti-6Al-4V instead of
structural steel? I modelled a generic 4.2 m ladder frame in FreeCAD, analysed it in Ansys Mechanical
2026 R1 (Student) as a shell model, and compared a steel baseline with three titanium versions.

**Main finding:** the answer depends entirely on what limits the design.

- If strength limits it, titanium wins big. A 2 mm Ti frame matches the steel frame's safety factor at
  **77 % less mass** (39 kg vs 174 kg).
- If stiffness limits it, titanium saves almost nothing. Ti's Young's modulus is only 57 % of steel's, so
  a Ti frame as stiff as the steel one needs 8.8 mm walls and weighs **172 kg**.
- In between, the thin Ti frames bring new problems. The 2 mm frame sags 4.6 times as much on a bump,
  twists about 8 times as much, and buckles at 2.4 times the design bump load, well before it would yield.

![Comparison](images/comparison.png)

## The model

| Item | Value |
| --- | --- |
| Frame | Two rails, 4200 mm long, 860 mm apart; five crossmembers |
| Rails | Rectangular hollow section 150 x 60 mm (midline) |
| Crossmembers | RHS 80 x 60 mm (midline) |
| Axle mounts | 100 mm pads under each rail at x = 700 mm (front) and 3500 mm (rear); 2800 mm wheelbase |
| Loads on frame | Cab + powertrain 1100 kg over x = 500 to 2400 mm; payload 1500 kg over x = 2400 to 4200 mm; frame self-weight |
| Mesh | Quadratic shell elements, 15 mm, about 72 000 nodes (inside the Student 128k limit) |
| Joints | Surfaces joined along shared edges with a mesh connection group (welded joints) |

Materials (linear elastic):

| Material | E (GPa) | Poisson | Density (kg/m3) | Yield (MPa) |
| --- | --- | --- | --- | --- |
| Steel S355 | 200 | 0.30 | 7850 | 355 |
| Ti-6Al-4V (annealed) | 113.8 | 0.342 | 4430 | 880 |

### Load cases

1. **Bump, 2.5 g.** All loads and the frame's own weight multiplied by 2.5. Rear mounts are pinned and the
   front mounts restrained vertically only. All supports are remote displacements, so rotations are free and
   the pads don't clamp the rail.
2. **Diagonal lift, 1 g.** The front-left wheel is off the ground, so the frame rests on three mounts and
   twists under its normal 1 g load.

## Results

| Design | Walls, rail / cross (mm) | Mass (kg) | Bump: far-field stress (MPa) | Bump SF | Diagonal: far-field stress (MPa) | Diagonal SF | Bump sag (mm) | Diagonal corner drop (mm) | Buckling load factor (bump) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Steel S355 (baseline) | 5.0 / 4.0 | 173.6 | 86.9 | 4.1 | 104.6 | 3.4 | 4.5 | 24.1 | > 50 |
| Ti-6Al-4V, strength-matched | 2.0 / 1.6 | 39.2 | 213.4 | 4.1 | 281.3 | 3.1 | 20.7 | 188 * | **2.4** |
| Ti-6Al-4V, 3 mm | 3.0 / 2.5 | 59.3 | 139.2 | 6.3 | 171.1 | 5.1 | 13.2 | 93 | 8.1 |
| Ti-6Al-4V, stiffness-matched | 8.8 / 7.0 | 172.3 | 50.3 | 17.5 | 50.9 | 17.3 | 4.5 | 18.3 | > 50 |

SF is yield divided by far-field von Mises stress. "Far-field" means every node more than 50 mm from a
crossmember joint or an axle-mount pad (see `analysis/farfield.py`). The buckling load factor comes from an
eigenvalue buckling analysis pre-stressed by the bump case; 2.4 means the 2 mm frame's rail web buckles at
2.4 x 2.5 g, about 6 g.

\* Linear analysis. A 188 mm corner drop is past the range where small-deflection results are reliable;
read it as "very flexible", not as an exact number.

| Steel, bump 2.5 g | Steel, diagonal lift |
| --- | --- |
| ![](images/steel_t5_Bump_25g_Von_Mises.jpg) | ![](images/steel_t5_Diagonal_lift_1g_Total_deformation.jpg) |
| **Ti-6Al-4V 2 mm, bump 2.5 g (deformation)** | **Ti-6Al-4V 2 mm, diagonal lift (stress)** |
| ![](images/ti_t2_Bump_25g_Total_deformation.jpg) | ![](images/ti_t2_Diagonal_lift_1g_Von_Mises.jpg) |

### Joint hot spots

The peak stresses sit at the crossmember-to-rail joints and at the mount pads, and they are much higher than
the far-field values: 451 MPa in the steel frame under diagonal lift, and 1863 MPa in the 2 mm Ti frame. In a
shell model these corners are stress singularities. Refining the mesh from 15 mm to 12 mm raised the steel
joint peak from 451 to 500 MPa, while the far-field stress didn't move (104.6 to 104.4 MPa). So I don't use the
peaks for the safety factor. They still matter: they say the joints need gussets or brackets. For the thin Ti
frames that local detail work, plus weld quality in titanium, would be a large part of the real design effort.

![Steel frame, diagonal lift: stress concentrates at the crossmember joints](images/steel_t5_Diagonal_lift_1g_Von_Mises.jpg)

## Checks

| Check | Result |
| --- | --- |
| Beam theory vs FEA, steel bump stress | 83.4 MPa hand calc vs 86.9 MPa FEA (+4 %) |
| Beam theory vs FEA, steel bump sag | 4.40 mm (1D beam FE) vs 4.54 mm (+3 %) |
| Same comparison, Ti 2 / 3 / 8.8 mm | Stress +6 / +3 / +6 %, sag +11 / +6 / +2 % (shell model adds shear and local wall bending) |
| Reaction sum, steel bump | 68 024 N = applied 63 765 N + 2.5 x 173.6 kg x g |
| Reaction sum, steel diagonal lift | 27 209 N = applied 25 506 N + 173.6 kg x g |
| Mesh 15 mm vs 12 mm (steel) | Far-field stress 86.9 vs 87.0 MPa (bump), sag 4.537 vs 4.537 mm |
| Frame mass | FEA 173.6 kg; by hand, rails 138.5 kg + crossmembers 35.2 kg = 173.7 kg |

Hand calculations are in `analysis/handcalc.py`.

## Limitations

- Linear static analysis. No fatigue check, and fatigue usually governs real chassis rails, especially at welds.
- Generic geometry and loads, not a specific vehicle. The supports are idealised pads, not spring hangers.
- No weld modelling, gussets or brackets at the joints.
- Cost isn't modelled. Titanium stock and welding cost many times more than steel.

## Native CAD and ANSYS files

These were generated by Claude (an AI assistant) on my machine, through FreeCAD and Ansys Mechanical, as GUI-ready versions of the scripted model above.

- `cad/ladder_frame_parametric.FCStd`: FreeCAD 1.1 PartDesign model. Each rail and the crossmembers are sketched sections padded to length, and every dimension is driven by the `Params` spreadsheet, so changing wall thickness or length there rebuilds the frame. Solid mass in steel: 173.4 kg, matching the shell model (173.6 kg).
- `cad/ladder_frame_solid.step`: the solid frame for other CAD tools.
- `cad/ladder_frame_drawing.pdf`: A3 drawing with orthographic and isometric views.
- `ansys_project/chassis_steel_vs_titanium.mechdb`: the Mechanical 2026 R1 model with geometry, mesh connections, both load cases and the buckling analysis (steel baseline). Open it in Mechanical and solve to regenerate results.

## Files

```
freecad/build_chassis.py      FreeCAD script: midsurface geometry, exports chassis_midsurface.step
ansys/01_import.py            Mechanical: import STEP and materials.xml
ansys/02_mesh_connections.py  Mechanical: join the 86 surface bodies along shared edges
ansys/03_model.py             Mechanical: named selections, loads, supports, result objects
ansys/04_solve_variant.py     Mechanical: set material/thickness from variant.json, mesh, solve, export
ansys/05_export_nodes.py      Mechanical: node coordinates for the far-field stress filter
ansys/mech_run.py             Sends a script to a running Mechanical session through PyMechanical
analysis/handcalc.py          Beam-theory checks
analysis/farfield.py          Separates joint hot spots from far-field stress
analysis/summarize.py         Builds results/summary.json
analysis/make_charts.py       Draws images/comparison.png
results/                      Raw Ansys results for each design, plus summary.json
```

To rerun, start Mechanical with gRPC enabled
(`AnsysWBU.exe -DSApplet -AppModeMech -grpc 10000 --transport-mode wnua`), run the `ansys/` scripts in
order with `python mech_run.py <script>`, then run `04_solve_variant.py` once per `variant.json`.

## Background

During my internship at Deccan Auto (Dec 2022 to May 2023) I worked on a team project on the design and
analysis of an armed-vehicle chassis in titanium. This repository is a fresh, independent study of the same
question. It uses generic geometry and loads, and none of the company's design or data.

---
Sai Phanidhar Ammiraju · [More projects](https://github.com/Saiphani02) · [LinkedIn](https://www.linkedin.com/in/sai-ammiraju)
