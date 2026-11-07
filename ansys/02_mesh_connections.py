# Runs inside Ansys Mechanical after 01_import.py.
# The STEP file arrives as 86 separate surface bodies (one per face). A mesh connection group
# joins their meshes along shared edges so the frame behaves as one welded structure.
me = Model.MeshEdit
if me is None:
    me = Model.AddMeshEdit()
for c in list(me.Children):
    c.Delete()
mc = me.AddMeshConnectionGroup()
ids = [b.Id for a in ExtAPI.DataModel.GeoData.Assemblies for p in a.Parts for b in p.Bodies]
s = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
s.Ids = ids
mc.Location = s
mc.ToleranceValue = Quantity(2.0, "mm")
mc.DetectConnections()
"mesh connections: %d" % mc.Children.Count     # 86
