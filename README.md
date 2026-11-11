# Ladder-frame chassis FEA: steel vs titanium

I modeled a 4.2 m truck ladder frame in FreeCAD and analyzed it in ANSYS Mechanical to answer one question: if you swap S355 steel for Ti-6Al-4V, how much weight do you actually save?

**Tools:** FreeCAD (Part Design) · ANSYS Mechanical 2026 R1

![Chassis drawing](images/drawing.png)

## Short answer

It depends on what limits the design.

- **Sized for strength**, titanium is a big win. A 2 mm Ti frame matches the steel frame's safety factor and weighs 39 kg instead of 174 kg (77% lighter).
- **Sized for stiffness**, it saves almost nothing. Titanium's Young's modulus is 57% of steel's, so a frame as stiff as the steel one needs 8.8 mm walls and weighs 172 kg.
- **The thin Ti frame has its own problems.** At 2 mm it sags 4.6x more on a bump, twists about 8x more, and has a linear buckling factor of 2.4 under the 2.5 g load.

## CAD model (FreeCAD)

- Two rails, hollow 150 x 60 mm section with 5 mm wall, 4200 mm long.
- Five crossmembers, hollow 80 x 60 mm section with 4 mm wall.
- Every dimension is driven from a `Params` spreadsheet, so each titanium variant is a spreadsheet edit rather than a new model.
- Mass check: 173.4 kg in steel from CAD, 173.6 kg from the FEA model.
- Exported as a solid STEP, a midsurface STEP for the shell analysis, and an A3 drawing.

## FEA setup (ANSYS Mechanical)

**Materials**

| Material | E (GPa) | Poisson's ratio | Density (kg/m³) | Yield (MPa) |
|---|---|---|---|---|
| Steel S355 | 200 | 0.30 | 7850 | 355 |
| Ti-6Al-4V (annealed) | 113.8 | 0.342 | 4430 | 880 |

**Model**

- Midsurface geometry meshed with quadratic shell elements, 15 mm size, about 72,000 nodes
- Rails and crossmembers joined along shared edges with mesh connections (welded joints)
- Axle mounts: 100 mm pads under each rail at x = 700 mm and 3500 mm (2800 mm wheelbase), pinned with remote displacements
- Cab and powertrain: 1100 kg spread over x = 500 to 2400 mm
- Payload: 1500 kg spread over x = 2400 to 4200 mm
- Frame self-weight included

**Load cases**

1. **Bump, 2.5 g.** All loads and self-weight multiplied by 2.5. Rear mounts pinned, front mounts held vertically only.
2. **Diagonal lift, 1 g.** Front-left wheel off the ground, so the frame sits on three mounts and twists.
3. **Eigenvalue buckling**, pre-stressed by the bump case.

## Results

| Design | Walls, rail / cross (mm) | Mass (kg) | Bump stress (MPa) | Bump SF | Twist stress (MPa) | Twist SF | Bump sag (mm) | Twist corner drop (mm) | Buckling factor |
|---|---|---|---|---|---|---|---|---|---|
| Steel S355 (baseline) | 5.0 / 4.0 | 173.6 | 86.9 | 4.1 | 104.6 | 3.4 | 4.5 | 24.1 | to be checked |
| Ti-6Al-4V, same strength | 2.0 / 1.6 | 39.2 | 213.4 | 4.1 | 281.3 | 3.1 | 20.7 | 188* | 2.4 |
| Ti-6Al-4V, 3 mm | 3.0 / 2.5 | 59.3 | 139.2 | 6.3 | 171.1 | 5.1 | 13.2 | 93 | 8.1 |
| Ti-6Al-4V, same stiffness | 8.8 / 7.0 | 172.3 | 50.3 | 17.5 | 50.9 | 17.3 | 4.5 | 18.3 | to be checked |

Stresses are far-field von Mises values, read more than 50 mm away from any joint or mount pad. SF is yield strength divided by that stress.

\* This is a linear analysis. A 188 mm corner drop is past where small-deflection results hold, so read it as "very flexible" rather than an exact number.

**Buckling note:** the steel and 8.8 mm Ti models returned negative eigenvalues (-51.9 and -77.2). A negative factor points to reversed loading or a different mode, so I haven't reported a positive buckling factor for those two until the modes are checked in Mechanical. The 2.43 for the 2 mm Ti frame is a linear eigenvalue result, not a predicted collapse load.

![Mass and stiffness comparison](images/comparison.png)

| Steel, bump 2.5 g | Steel, diagonal lift |
|---|---|
| ![](images/steel_t5_Bump_25g_Von_Mises.jpg) | ![](images/steel_t5_Diagonal_lift_1g_Total_deformation.jpg) |
| **Ti-6Al-4V 2 mm, bump 2.5 g (deformation)** | **Ti-6Al-4V 2 mm, diagonal lift (stress)** |
| ![](images/ti_t2_Bump_25g_Total_deformation.jpg) | ![](images/ti_t2_Diagonal_lift_1g_Von_Mises.jpg) |

## The joints

The highest stresses sit where crossmembers meet the rails and at the mount pads: 451 MPa in the steel frame under diagonal lift, 1863 MPa in the 2 mm Ti frame. In a shell model those sharp corners are singularities. Refining the mesh from 15 mm to 12 mm pushed the steel joint peak from 451 to 500 MPa while the far-field stress didn't move (104.6 vs 104.4 MPa), so I don't use the peaks for safety factors.

What they do tell me is that the joints need gussets or brackets. For thin titanium, that detail work and weld quality would be a big part of a real design.

![Steel frame, diagonal lift: stress concentrates at the crossmember joints](images/steel_t5_Diagonal_lift_1g_Von_Mises.jpg)

## Checks

| Check | Result |
|---|---|
| Hand beam calc vs FEA, steel bump stress | 83.4 MPa vs 86.9 MPa (+4%) |
| Hand beam calc vs FEA, steel bump sag | 4.40 mm vs 4.54 mm (+3%) |
| Same for Ti 2 / 3 / 8.8 mm | Stress +6 / +3 / +6%, sag +11 / +6 / +2% (the shell model adds shear and local wall bending) |
| Reactions, steel bump | 68,024 N = 63,765 N applied + 2.5 x 173.6 kg x g |
| Reactions, steel diagonal lift | 27,209 N = 25,506 N applied + 173.6 kg x g |
| Mesh 15 mm vs 12 mm | Far-field stress 86.9 vs 87.0 MPa, sag 4.537 vs 4.537 mm |
| Frame mass | CAD 173.4 kg, FEA 173.6 kg, hand calc 173.7 kg |

## Limitations

- Linear static only. There's no fatigue check, and fatigue usually governs real chassis rails, especially at the welds.
- Generic geometry and loads, not a specific vehicle. Supports are idealized pads, not leaf-spring hangers.
- Welds, gussets and brackets at the joints are not modeled.
- Cost isn't considered. Titanium stock and welding cost many times more than steel.

## Files

| File | What it is |
|---|---|
| [cad/ladder_frame_parametric.FCStd](cad/ladder_frame_parametric.FCStd) | FreeCAD model with the Params spreadsheet |
| [cad/ladder_frame_solid.step](cad/ladder_frame_solid.step) | Solid geometry for any CAD tool |
| [cad/chassis_midsurface.step](cad/chassis_midsurface.step) | Midsurface geometry used for the shell analysis |
| [cad/ladder_frame_drawing.pdf](cad/ladder_frame_drawing.pdf) | A3 engineering drawing |
| [ansys_project/chassis_steel_vs_titanium.mechdb](ansys_project/chassis_steel_vs_titanium.mechdb) | ANSYS Mechanical model (open in Mechanical 2026 R1) |
| [results/results.csv](results/results.csv) | Results for all four designs |
| [images/](images/) | Drawing, contour plots and comparison chart |

To download everything, use **Code → Download ZIP**.

## Background

During my internship at Deccan Auto (Dec 2022 to May 2023) I worked on a team project on the design and analysis of an armed-vehicle chassis in titanium. This repository is a separate, independent study of the same question with generic geometry and loads. None of the company's design or data is used.

---

Sai Phanidhar Ammiraju · [Portfolio](https://saiphani02.github.io) · [LinkedIn](https://www.linkedin.com/in/sai-ammiraju)
