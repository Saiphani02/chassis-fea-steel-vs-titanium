# Runs inside Ansys Mechanical after 01_import.py and 02_mesh_connections.py.
# Builds: named selections, material/thickness, mesh settings, two static analyses and result objects
#   A1 "Bump 2.5g"  : 2.5 g vertical on sprung loads + frame self weight
#   A2 "Diagonal lift 1g": front-left wheel off the ground, 1 g loads, 3-point support
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM
DM = Ansys.Mechanical.DataModel.Enums
log = []

def sel(ids):
    s = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    s.Ids = ids
    return s

# ---------- classify faces --------------------------------------------------
faces = []
for asm in ExtAPI.DataModel.GeoData.Assemblies:
    for part in asm.Parts:
        for body in part.Bodies:
            for f in body.Faces:
                faces.append(f)
groups = dict(RAILS=[], CROSS=[], LOAD_FRONT=[], LOAD_REAR=[],
              MOUNT_FL=[], MOUNT_FR=[], MOUNT_RL=[], MOUNT_RR=[])
for f in faces:
    x, y, z = [c for c in f.Centroid]          # GeoData centroid in active units (mm)
    if abs(y) < 399.0:
        groups["CROSS"].append(f.Id)
        continue
    groups["RAILS"].append(f.Id)
    if abs(z - 75.0) < 1.0:
        if 500.0 < x < 2400.0: groups["LOAD_FRONT"].append(f.Id)
        elif 2400.0 < x < 4200.0: groups["LOAD_REAR"].append(f.Id)
    if abs(z + 75.0) < 1.0:
        side = "L" if y > 0 else "R"
        if 650.0 < x < 750.0: groups["MOUNT_F" + side].append(f.Id)
        if 3450.0 < x < 3550.0: groups["MOUNT_R" + side].append(f.Id)
log.append(str({k: len(v) for k, v in groups.items()}))

existing = {}
if Model.NamedSelections is not None:
    for n in Model.NamedSelections.Children:
        existing[n.Name] = n
NS = {}
for k, ids in groups.items():
    n = existing.get(k) or Model.AddNamedSelection()
    n.Name = k
    n.Location = sel(ids)
    NS[k] = n

# ---------- material + thickness per body (each imported face is its own surface body) ---
mats = [m.Name for m in Model.Materials.Children]
log.append("materials: " + ", ".join(mats))
cross_ids = set(groups["CROSS"])
for b in Model.GetChildren(DataModelObjectCategory.Body, True):
    gb = b.GetGeoBody()
    b.Material = "Steel S355"
    b.Thickness = Quantity(4.0 if gb.Faces[0].Id in cross_ids else 5.0, "mm")

# ---------- mesh ------------------------------------------------------------
mesh = Model.Mesh
mesh.ElementSize = Quantity(15.0, "mm")
mesh.ElementOrder = DM.ElementOrder.Quadratic

# ---------- analyses ----------------------------------------------------------
an = {a.Name: a for a in Model.Analyses}
def get_an(name):
    if name in an:
        return an[name]
    a = Model.AddStaticStructuralAnalysis()
    a.Name = name
    return a

g = 9810.0      # mm/s^2
A1 = get_an("Bump 2.5g")
A2 = get_an("Diagonal lift 1g")
for a in (A1, A2):
    for c in list(a.Children):
        if c.DataModelObjectCategory in (DataModelObjectCategory.Force, DataModelObjectCategory.Displacement,
                                         DataModelObjectCategory.Acceleration, DataModelObjectCategory.FixedSupport,
                                         DataModelObjectCategory.RemoteDisplacement):
            c.Delete()

def pin(a, ns_name, free_x=False):
    # remote displacement at the mount pad: translations fixed, rotations free (pin, no clamping)
    d = a.AddRemoteDisplacement()
    d.Location = NS[ns_name]
    d.Name = "Mount " + ns_name[-2:]
    d.ZComponent.Output.DiscreteValues = [Quantity(0, "mm")]
    if not free_x:
        d.XComponent.Output.DiscreteValues = [Quantity(0, "mm")]
        d.YComponent.Output.DiscreteValues = [Quantity(0, "mm")]
    return d

def zforce(a, ns_name, newton, name):
    f = a.AddForce()
    f.Location = NS[ns_name]
    f.DefineBy = DM.LoadDefineBy.Components
    f.ZComponent.Output.DiscreteValues = [Quantity(newton, "N")]
    f.Name = name
    return f

def accel(a, factor):
    ac = a.AddAcceleration()
    ac.DefineBy = DM.LoadDefineBy.Components
    ac.ZComponent.Output.DiscreteValues = [Quantity(factor * g, "mm s^-2")]
    ac.Name = "Frame self weight x%.1f" % factor

# A1: rear mounts pinned, front mounts vertical only (no over-constraint along the rail)
pin(A1, "MOUNT_RL"); pin(A1, "MOUNT_RR"); pin(A1, "MOUNT_FL", True); pin(A1, "MOUNT_FR", True)
zforce(A1, "LOAD_FRONT", -2.5 * 1100 * 9.81, "Cab + powertrain 1100 kg x2.5")
zforce(A1, "LOAD_REAR",  -2.5 * 1500 * 9.81, "Payload 1500 kg x2.5")
accel(A1, 2.5)

# A2: diagonal wheel lift - front-left wheel off the ground, 1 g loads, 3-point support
pin(A2, "MOUNT_RL"); pin(A2, "MOUNT_RR"); pin(A2, "MOUNT_FR", True)
zforce(A2, "LOAD_FRONT", -1100 * 9.81, "Cab + powertrain 1100 kg x1.0")
zforce(A2, "LOAD_REAR",  -1500 * 9.81, "Payload 1500 kg x1.0")
accel(A2, 1.0)

# ---------- results -----------------------------------------------------------
for a in (A1, A2):
    s = a.Solution
    for c in list(s.Children):
        if c.DataModelObjectCategory != DataModelObjectCategory.SolutionInformation and hasattr(c, "Delete"):
            c.Delete()
    r = s.AddEquivalentStress(); r.Name = "Von Mises"
    r = s.AddEquivalentStress(); r.Name = "Von Mises rails"; r.Location = NS["RAILS"]
    r = s.AddEquivalentStress(); r.Name = "Von Mises crossmembers"; r.Location = NS["CROSS"]
    r = s.AddTotalDeformation(); r.Name = "Total deformation"
    r = s.AddDirectionalDeformation(); r.Name = "Vertical deflection"
    r.NormalOrientation = DM.NormalOrientationType.ZAxis
    for bc in a.Children:
        if bc.DataModelObjectCategory in (DataModelObjectCategory.Displacement, DataModelObjectCategory.RemoteDisplacement):
            f = s.AddForceReaction(); f.Name = "Reaction " + bc.Name
            f.BoundaryConditionSelection = bc
"\n".join(log)
