import numpy as np

from .ponto import Ponto
from .quadrilatero import Quadrilatero
from .tdma import calcular_tdma
from .util import print_title, max_val, min_val


def calcular_KK(n, E, debug=0):
    E_np = np.asarray(E, dtype=float)  # (n, n)
    dim  = n + 1

    Kx = np.zeros((dim, dim))
    # j == n  →  0  (already zero)
    # i == 0  →  E[0, j]
    Kx[0,  :n] = E_np[0, :]
    # i == n  →  E[n-1, j]
    Kx[n,  :n] = E_np[n - 1, :]
    # 1 ≤ i ≤ n-1  →  avg(E[i-1,j], E[i,j])
    Kx[1:n, :n] = (E_np[:-1, :] + E_np[1:, :]) / 2.0

    Ky = np.zeros((dim, dim))
    # i == n  →  0  (already zero)
    # j == 0  →  E[i, 0]
    Ky[:n, 0] = E_np[:, 0]
    # j == n  →  E[i, n-1]
    Ky[:n, n] = E_np[:, n - 1]
    # 1 ≤ j ≤ n-1  →  avg(E[i,j-1], E[i,j])
    Ky[:n, 1:n] = (E_np[:, :-1] + E_np[:, 1:]) / 2.0

    return Kx, Ky


def calcular_XY(n, Kx, Ky, debug=0):
    """Return X, Y as (n+1)×(n+1) numpy arrays.

    Boundary conditions built internally:
      Vx: left col = 0, right col = 1  (X fixed)
      Vy: top row  = 0, bottom row = 1 (Y fixed)
    """
    dim = n + 1

    # Initial guess: uniform grid
    j_lin = np.linspace(0.0, 1.0, dim)
    i_lin = np.linspace(0.0, 1.0, dim)
    X = np.tile(j_lin, (dim, 1))          # X[i,j] = j/n
    Y = np.tile(i_lin[:, None], (1, dim)) # Y[i,j] = i/n

    # Boundary masks (True = Dirichlet)
    Vx_bnd = np.zeros((dim, dim), dtype=bool)
    Vx_bnd[:, 0] = True
    Vx_bnd[:, n] = True
    Vx_vals = np.zeros((dim, dim))
    Vx_vals[:, n] = 1.0

    Vy_bnd = np.zeros((dim, dim), dtype=bool)
    Vy_bnd[0, :] = True
    Vy_bnd[n, :] = True
    Vy_vals = np.zeros((dim, dim))
    Vy_vals[n, :] = 1.0

    # Coefficient matrices (shared for X and Y solves)
    aP, aE, aN, aW, aS, bP = _build_coeffs(n, Kx, Ky, dim)

    calcular_tdma(X, aP, aE, aN, aW, aS, bP, Vx_bnd, Vx_vals, dim, 3, debug - 1)
    calcular_tdma(Y, aP, aE, aN, aW, aS, bP, Vy_bnd, Vy_vals, dim, 3, debug - 1)

    return X, Y


def _build_coeffs(n, Kx, Ky, dim):
    aE = Kx.copy()
    aS = Ky.copy()

    aW = np.zeros((dim, dim))
    aW[:, 1:] = Kx[:, :-1]

    aN = np.zeros((dim, dim))
    aN[1:, :] = Ky[:-1, :]

    aP = aW + aN + aE + aS
    bP = np.zeros((dim, dim))

    return aP, aE, aN, aW, aS, bP


def calcular_soma(n, X, Y, E, debug=0):
    X_np = np.asarray(X)
    Y_np = np.asarray(Y)
    E_np = np.asarray(E, dtype=float)

    x00, x01 = X_np[:n, :n], X_np[:n, 1:]
    x10, x11 = X_np[1:, :n], X_np[1:, 1:]
    y00, y01 = Y_np[:n, :n], Y_np[:n, 1:]
    y10, y11 = Y_np[1:, :n], Y_np[1:, 1:]

    ux, uy = x00 - x01, y00 - y01
    vx, vy = x10 - x01, y10 - y01
    wx, wy = x11 - x01, y11 - y01

    area_s = (ux * vy - vx * uy + wx * vy - vx * wy) / 2.0
    prod   = area_s * E_np
    soma   = float(np.where(prod > 0, prod, -1000.0 * prod).sum())

    if debug > 0:
        print(f"\n#soma={soma}")
    return soma


# ── legacy helpers (not called by the main EA loop) ──────────────────────────

def calcular_desvio(n, X, Y, E, debug=0):
    if debug > 0:
        print_title("Cálculo do desvio - diferença entre máximo e mínimo")
    maximo = -1.0
    minimo = 1e100
    for i in range(n):
        for j in range(n):
            quad = Quadrilatero(
                Ponto(X[i][j],     Y[i][j]),
                Ponto(X[i][j+1],   Y[i][j+1]),
                Ponto(X[i+1][j],   Y[i+1][j]),
                Ponto(X[i+1][j+1], Y[i+1][j+1]),
            )
            prod = quad.areaS() * E[i][j]
            maximo = max_val(maximo, prod)
            minimo = min_val(minimo, prod)
    return n * n * (maximo - minimo)


def calcular_desvio_padrao(n, X, Y, E, debug=0):
    import math
    X_np = np.asarray(X); Y_np = np.asarray(Y); E_np = np.asarray(E, dtype=float)
    x00, x01 = X_np[:n, :n], X_np[:n, 1:]
    x10, x11 = X_np[1:, :n], X_np[1:, 1:]
    y00, y01 = Y_np[:n, :n], Y_np[:n, 1:]
    y10, y11 = Y_np[1:, :n], Y_np[1:, 1:]
    ux, uy = x00-x01, y00-y01
    vx, vy = x10-x01, y10-y01
    wx, wy = x11-x01, y11-y01
    area_s = (ux*vy - vx*uy + wx*vy - vx*wy) / 2.0
    prod = area_s * E_np
    return float(np.sqrt(((prod - prod.mean())**2).mean()))


def calcular_maximo(n, X, Y, E, debug=0):
    X_np = np.asarray(X); Y_np = np.asarray(Y); E_np = np.asarray(E, dtype=float)
    x00, x01 = X_np[:n, :n], X_np[:n, 1:]
    x10, x11 = X_np[1:, :n], X_np[1:, 1:]
    y00, y01 = Y_np[:n, :n], Y_np[:n, 1:]
    y10, y11 = Y_np[1:, :n], Y_np[1:, 1:]
    ux, uy = x00-x01, y00-y01
    vx, vy = x10-x01, y10-y01
    wx, wy = x11-x01, y11-y01
    area_s = (ux*vy - vx*uy + wx*vy - vx*wy) / 2.0
    return float(n * n * (area_s * E_np).max())
