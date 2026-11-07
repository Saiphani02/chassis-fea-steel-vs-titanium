import sys, collections
nodes = {}
import os
for l in open(os.environ.get("NODES","nodes.txt")):
    p = l.split()
    if len(p) != 4: continue
    i,x,y,z = p; nodes[int(i)] = (float(x),float(y),float(z))
sc = 1000.0 if max(abs(v[0]) for v in nodes.values()) < 10 else 1.0
xs_cm=[30.,900.,2100.,3300.,4170.]; mounts=[700.,3500.]
def near_joint(x,y,z,d):
    if any(abs(x-xc) < 30+d for xc in xs_cm) and (abs(abs(y)-400) < d or abs(y) < 400):   # crossmember zone incl. rail web patch
        return True
    if any(abs(x-xm) < 50+d for xm in mounts) and abs(abs(y)-430) < 31: return True
    return False
def stats(fn, d):
    vals = collections.defaultdict(float)
    for l in open(fn).readlines()[1:]:
        p = l.split()
        if len(p) < 2: continue
        i, v = int(p[0]), float(p[1]); vals[i] = max(vals[i], v)
    allmax = max(vals.values())
    ff = [v for i,v in vals.items() if i in nodes and not near_joint(*[c*sc for c in nodes[i]], d)]
    ff.sort()
    return allmax, ff[-1], ff[int(0.99*len(ff))]
for fn in sys.argv[1:]:
    for d in (50, 100):
        a, m, p99 = stats(fn, d)
        print("%s  excl %d mm: peak %.1f | far-field max %.1f | far-field 99th pct %.1f MPa" % (fn, d, a, m, p99))
