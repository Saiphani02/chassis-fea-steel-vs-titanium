# Engineering verification notes

This repository documents a comparative shell-element FEA study of a ladder-frame chassis. The following items remain to be checked against the native ANSYS Mechanical solution before treating all reported values as independently validated.

1. **Buckling eigenvalues:** `results/summary.json` reports negative factors for the steel and 8.8 mm titanium variants (-51.89 and -77.21). Inspect eigenmodes, load direction, solver settings and the positive spectrum; negative values are not evidence of a positive-load buckling factor greater than 50.
2. **Model setup:** Verify shell connections at the rail/crossmember interfaces, remote displacement constraints and the load distribution at mount pads.
3. **Stress reporting:** Confirm the 50 mm far-field exclusion and mesh-convergence comparison against the saved results.
4. **Reproducibility:** Rerun the automation scripts in the intended FreeCAD and ANSYS versions, comparing generated JSON and figures with the committed outputs.
5. **Scope:** The study uses idealized static loading, omits detailed welds and fatigue, and does not establish production readiness.

These notes document outstanding technical verification, not changes to the underlying simulation data.
