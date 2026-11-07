"""Builds the ladder-frame midsurface model in FreeCAD 1.1 and exports it as STEP.

Run in the FreeCAD Python console (or through the FreeCAD MCP server).
All dimensions are midline (sheet-metal midsurface) values in mm.
"""
import os
import FreeCAD as App
import Part
import Import
from FreeCAD import Vector as V

OUT = os.path.expanduser("~/Documents/Chassis_Study")
os.makedirs(OUT, exist_ok=True)

L = 4200.0           # frame length
YC = 430.0           # rail centreline offset from vehicle centreline (860 mm between rails)
H, B = 150.0, 60.0   # rail RHS 150 x 60
CH, CW = 80.0, 60.0  # crossmember RHS 80 x 60
XS_CM = [30.0, 900.0, 2100.0, 3300.0, 4170.0]       # crossmember stations
BRK = [0.0, 500.0, 650.0, 750.0, 2400.0, 3450.0, 3550.0, 4200.0]  # face splits: load zones and axle mount pads


def quad(p1, p2, p3, p4):
    return Part.Face(Part.makePolygon([p1, p2, p3, p4, p1]))


faces = []
for s in (-1, 1):
    y0 = s * YC
    for x0, x1 in zip(BRK[:-1], BRK[1:]):
        faces += [
            quad(V(x0, y0 - B / 2, H / 2), V(x1, y0 - B / 2, H / 2), V(x1, y0 + B / 2, H / 2), V(x0, y0 + B / 2, H / 2)),      # top flange
            quad(V(x0, y0 - B / 2, -H / 2), V(x1, y0 - B / 2, -H / 2), V(x1, y0 + B / 2, -H / 2), V(x0, y0 + B / 2, -H / 2)),  # bottom flange
            quad(V(x0, y0 - B / 2, -H / 2), V(x1, y0 - B / 2, -H / 2), V(x1, y0 - B / 2, H / 2), V(x0, y0 - B / 2, H / 2)),    # web
            quad(V(x0, y0 + B / 2, -H / 2), V(x1, y0 + B / 2, -H / 2), V(x1, y0 + B / 2, H / 2), V(x0, y0 + B / 2, H / 2)),    # web
        ]
YI = YC - B / 2      # inner web plane, where crossmembers meet the rails
for xc in XS_CM:
    xa, xb = xc - CW / 2, xc + CW / 2
    faces += [
        quad(V(xa, -YI, CH / 2), V(xb, -YI, CH / 2), V(xb, YI, CH / 2), V(xa, YI, CH / 2)),
        quad(V(xa, -YI, -CH / 2), V(xb, -YI, -CH / 2), V(xb, YI, -CH / 2), V(xa, YI, -CH / 2)),
        quad(V(xa, -YI, -CH / 2), V(xa, YI, -CH / 2), V(xa, YI, CH / 2), V(xa, -YI, CH / 2)),
        quad(V(xb, -YI, -CH / 2), V(xb, YI, -CH / 2), V(xb, YI, CH / 2), V(xb, -YI, CH / 2)),
    ]

# general fuse imprints the crossmember ends onto the rail webs so neighbouring faces share edges
pieces, _ = faces[0].generalFuse(faces[1:], 0.01)
doc = App.newDocument("Chassis")
obj = doc.addObject("Part::Feature", "LadderFrame")
obj.Shape = pieces
doc.recompute()
print("faces", len(obj.Shape.Faces), "area m2", round(obj.Shape.Area / 1e6, 3))   # 86 faces, 4.648 m2
Import.export([obj], os.path.join(OUT, "chassis_midsurface.step"))
doc.saveAs(os.path.join(OUT, "chassis.FCStd"))
