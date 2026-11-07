# Runs inside Ansys Mechanical: imports the midsurface STEP and the two custom materials.
import os
WORK = r"C:\Users\saiph\Documents\Chassis_Study"   # folder holding the STEP file, materials.xml and variant.json
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM
log = []
if Model.Geometry.Children.Count == 0:
    gi = Model.GeometryImportGroup.AddGeometryImport()
    pref = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
    pref.ProcessNamedSelections = True
    fmt = Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
    gi.Import(os.path.join(WORK, "chassis_midsurface.step"), fmt, pref)
if "Ti-6Al-4V" not in [m.Name for m in Model.Materials.Children]:
    Model.Materials.Import(os.path.join(WORK, "materials.xml"))     # adds "Steel S355" and "Ti-6Al-4V"
bodies = Model.GetChildren(DataModelObjectCategory.Body, True)
log.append("bodies=%d" % bodies.Count)
for b in bodies:
    log.append("%s type=%s faces=%d" % (b.Name, b.GeometryType, b.GetGeoBody().Faces.Count))
"\n".join(log)
