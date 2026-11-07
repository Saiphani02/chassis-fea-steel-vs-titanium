import json, os
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM
WORK = r"C:\Users\saiph\Documents\Chassis_Study"   # folder holding the STEP file, materials.xml and variant.json
VARIANT = json.loads(open(os.path.join(WORK, "variant.json")).read())
cross_ids = set([i for i in [n for n in Model.NamedSelections.Children if n.Name == "CROSS"][0].Location.Ids])
mass = 0.0
for b in Model.GetChildren(DataModelObjectCategory.Body, True):
    gb = b.GetGeoBody()
    b.Material = VARIANT["material"]
    b.Thickness = Quantity(VARIANT["t_cross"] if gb.Faces[0].Id in cross_ids else VARIANT["t_rail"], "mm")
Model.Mesh.ElementSize = Quantity(VARIANT.get('esize', 15.0), 'mm')
Model.Mesh.ClearGeneratedData()
Model.Mesh.GenerateMesh()
mcg = [c for c in Model.MeshEdit.Children][0]
res_mc = [(c.Name, str(c.ObjectState)) for c in list(mcg.Children)[:3]]
for b in Model.GetChildren(DataModelObjectCategory.Body, True):
    mass += b.Mass.Value
res = dict(VARIANT)
res["nodes"] = Model.Mesh.Nodes
res["elements"] = Model.Mesh.Elements
res["mass_kg"] = mass   # kg (StandardNMM reports body mass in kg)
res["mesh_connection_states"] = res_mc
for a in [x for x in Model.Analyses if x.AnalysisType != Ansys.Mechanical.DataModel.Enums.AnalysisType.Buckling]:
    try:
        a.AnalysisSettings.WeakSprings = Ansys.Mechanical.DataModel.Enums.WeakSpringsType.Off
    except Exception as e:
        res["weak_springs_err"] = str(e)[:100]
    a.Solution.ClearGeneratedData()
    a.Solve(True)
    r = {}
    for c in a.Solution.Children:
        if c.Name.startswith("Reaction"):
            r[c.Name] = c.ZAxis.Value
            continue
        if not hasattr(c, "Maximum"):
            continue
        try:
            r[c.Name] = dict(max=c.Maximum.Value, min=c.Minimum.Value, unit=str(c.Maximum.Unit))
        except Exception:
            pass
        try:
            occ = str(c.MaximumOccursOn)
            r[c.Name]["max_on"] = occ
            for b in Model.GetChildren(DataModelObjectCategory.Body, True):
                if b.Name == occ:
                    cc = b.GetGeoBody().Faces[0].Centroid
                    r[c.Name]["max_face_centroid"] = [round(v, 1) for v in cc]
        except Exception as e:
            r.setdefault("loc_err", str(e)[:120])
        if c.Name == "Von Mises":
            c.ExportToTextFile(os.path.join(WORK, "vm_%s_%s.txt" % (VARIANT["tag"], a.Name.replace(" ", "_").replace(".", ""))))
        if VARIANT.get("images") and c.Name in ("Von Mises", "Total deformation"):
            c.Activate()
            Graphics.Camera.SetSpecificViewOrientation(Ansys.Mechanical.DataModel.Enums.ViewOrientationType.Iso)
            Graphics.Camera.SetFit()
            st = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
            st.Width = 1600; st.Height = 900; st.CurrentGraphicsDisplay = False
            fn = os.path.join(WORK, "img_%s_%s_%s.png" % (VARIANT["tag"], a.Name.replace(" ", "_").replace(".", ""), c.Name.replace(" ", "_")))
            Graphics.ExportImage(fn, Ansys.Mechanical.DataModel.Enums.GraphicsImageExportFormat.PNG, st)
    r["status"] = str(a.Solution.Status)
    r["messages"] = [m.DisplayString[:200] for m in ExtAPI.Application.Messages if str(m.Severity) in ("Error","Warning")][-5:]
    res[a.Name] = r
if VARIANT.get("buckling"):
    bk = [x for x in Model.Analyses if x.AnalysisType == Ansys.Mechanical.DataModel.Enums.AnalysisType.Buckling]
    if bk:
        bk = bk[0]
    else:
        bk = Model.AddEigenvalueBucklingAnalysis()
        bk.Name = "Buckling (from bump)"
        bk.InitialConditions[0].PreStressICEnvironment = [x for x in Model.Analyses if x.Name == "Bump 2.5g"][0]
        bk.AnalysisSettings.MaximumModesToFind = 3
        td = bk.Solution.AddTotalDeformation(); td.Name = "Buckling mode 1"
    bk.Solution.ClearGeneratedData()
    bk.Solve(True)
    td = [c for c in bk.Solution.Children if c.Name == "Buckling mode 1"][0]
    res["buckling_load_multiplier_mode1"] = td.LoadMultiplier
    try:
        res["buckling_mode1_max_on"] = str(td.MaximumOccursOn)
    except Exception:
        pass
with open(os.path.join(WORK, "result_%s.json" % VARIANT["tag"]), "w") as fh:
    fh.write(json.dumps(res, indent=1))
json.dumps(res)
