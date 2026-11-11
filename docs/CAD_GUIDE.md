# Chassis CAD and simulation guide

## Download

Use **Code → Download ZIP** on the repository home page and extract the ZIP before opening the files. For one file, open its GitHub page and choose the raw-file download. Keep the original download and edit a working copy.

## File formats

STEP stores exchange geometry; it does not preserve the original sketch constraints or feature history. Native application files are the starting point for inspecting the editable model. Images and videos are previews; numerical tables are documented results.

## Open the CAD model

1. Open [ladder_frame_parametric.FCStd](../cad/ladder_frame_parametric.FCStd) in FreeCAD.
2. Inspect the Params spreadsheet, sketches, and pads described in the main README.
3. Use a separate copy for parameter changes and recompute before exporting.
4. For geometry exchange, use [ladder_frame_solid.step](../cad/ladder_frame_solid.step).
5. The [midsurface STEP](../cad/chassis_midsurface.step) is a separate surface representation for shell FEA; it is not the solid model.

## Drawing and simulation

- View the [A3 drawing](../cad/ladder_frame_drawing.pdf) and [drawing preview](../images/drawing.png).
- Use ANSYS Mechanical 2026 R1 to inspect the supplied [Mechanical database](../ansys_project/chassis_steel_vs_titanium.mechdb). This is a Mechanical database, not a complete Workbench archive.
- Before a new solve, inspect geometry links, material assignments, shell thicknesses, mesh connections, supports, loads, and solver settings.
- Compare against [summary.json](../results/summary.json) and the [published results and limitations](../README.md#results).

## Supporting automation

[automation/](../automation/) contains CAD generation, batch variant solves, numerical checks, stress filtering, and plots. Viewing the supplied CAD model, drawing, and result images does not require running these scripts. Reproducing the original batch processing uses the documented automation.

## Review status

This guide catalogs the repository files; it does not establish that they have been reopened or solved successfully on another installation. Check [REVIEW_NOTES.md](../REVIEW_NOTES.md) before interpreting the buckling results or treating the study as a validated design.
