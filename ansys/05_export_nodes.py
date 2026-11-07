# Runs inside Ansys Mechanical: writes node coordinates (mm) so analysis/farfield.py can locate
# each stress value and separate joint hot spots from the far-field stress.
md = ExtAPI.DataModel.MeshDataByName("Global")
lines = []
for i in md.NodeIds:
    n = md.NodeById(i)
    lines.append("%d %.3f %.3f %.3f" % (i, n.X, n.Y, n.Z))
with open(r"C:\Users\saiph\Documents\Chassis_Study\nodes.txt", "w") as fh:
    fh.write("\n".join(lines))
"nodes written %d" % len(lines)
