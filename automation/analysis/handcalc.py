"""Hand checks for the bump case: one rail treated as a beam on two supports (front and rear axle).

1. Bending stress from the bending moment diagram (sigma = M c / I).
2. Deflection from a 1D Euler-Bernoulli beam finite-element model (4200 elements).
Both use the same loads as the Ansys model, split equally between the two rails.
"""
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve

G = 9.81
L, XF, XR = 4200.0, 700.0, 3500.0                     # mm: frame length, front and rear axle mounts
ZONES = [(500.0, 2400.0, 1100.0), (2400.0, 4200.0, 1500.0)]   # (x0, x1, mass kg): cab+powertrain, payload
H, B = 150.0, 60.0
MATS = {"Steel S355": dict(E=200e3, Sy=355.0, rho=7850e-9), "Ti-6Al-4V": dict(E=113.8e3, Sy=880.0, rho=4430e-9)}


def rhs(h, b, t):
    """Thin-walled rectangular hollow section, midline dimensions: (I, A)."""
    return t * h**3 / 6 + 2 * b * t * (h / 2) ** 2, 2 * (h + b) * t


def line_load(x, A, rho, nfac):
    w = np.zeros_like(x)
    for x0, x1, m in ZONES:
        w[(x >= x0) & (x < x1)] += m * G / 2 / (x1 - x0)      # per rail, N/mm
    return nfac * (w + A * rho * G)


def bending(t, mat, nfac=2.5):
    I, A = rhs(H, B, t)
    x = np.linspace(0, L, 8401); dx = x[1] - x[0]
    w = line_load(x, A, MATS[mat]["rho"], nfac)
    W, Mw = np.trapezoid(w, x), np.trapezoid(w * x, x)
    Rr = (Mw - W * XF) / (XR - XF); Rf = W - Rr
    V = -np.cumsum(w) * dx + Rf * (x >= XF) + Rr * (x >= XR)
    M = np.cumsum(V) * dx
    sigma = np.abs(M).max() * (H / 2) / I
    return sigma, Rf, Rr


def deflection(t, mat, nfac=2.5, n=4200):
    I, A = rhs(H, B, t)
    E = MATS[mat]["E"]
    x = np.linspace(0, L, n + 1); h = x[1] - x[0]
    w = line_load(x, A, MATS[mat]["rho"], nfac)
    K = lil_matrix((2 * (n + 1), 2 * (n + 1))); F = np.zeros(2 * (n + 1))
    ke = E * I / h**3 * np.array([[12, 6*h, -12, 6*h], [6*h, 4*h*h, -6*h, 2*h*h],
                                  [-12, -6*h, 12, -6*h], [6*h, 2*h*h, -6*h, 4*h*h]])
    for e in range(n):
        d = [2*e, 2*e+1, 2*e+2, 2*e+3]
        for i in range(4):
            for j in range(4):
                K[d[i], d[j]] += ke[i, j]
        q = (w[e] + w[e+1]) / 2
        F[d] += -q * np.array([h/2, h*h/12, h/2, -h*h/12])
    fixed = {2 * int(round(XF / h)), 2 * int(round(XR / h))}
    free = [i for i in range(2 * (n + 1)) if i not in fixed]
    u = np.zeros(2 * (n + 1))
    u[free] = spsolve(K.tocsr()[free][:, free], F[free])
    return -u[0::2].min()


if __name__ == "__main__":
    for t, mat in [(5.0, "Steel S355"), (2.0, "Ti-6Al-4V"), (3.0, "Ti-6Al-4V"), (8.8, "Ti-6Al-4V")]:
        s, Rf, Rr = bending(t, mat)
        print("%-10s t=%.1f mm  sigma_max=%6.1f MPa  sag(2.5 g)=%5.2f mm  Rf=%.0f N  Rr=%.0f N per rail"
              % (mat, t, s, deflection(t, mat), Rf, Rr))
