import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve

from .ponto import Ponto
from .quadrilatero import Quadrilatero
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
    """Return X, Y as (n+1)×(n+1) numpy arrays via direct sparse solve.

    Assembles the 5-point diffusion stencil as a sparse linear system and
    solves it exactly with SuperLU — one solve for X (Vx BCs) and one for Y
    (Vy BCs).  Replaces the previous 3-iteration ADI approximation.
    """
    dim = n + 1
    N   = dim * dim

    aP, aE, aN, aW, aS, bP = _build_coeffs(n, Kx, Ky, dim)

    # Per-node row/col indices, shared between the two assemblies
    node = np.arange(N)
    i_arr, j_arr = np.divmod(node, dim)

    # Vx: left col (j=0) → T=0 ; right col (j=n) → T=1
    Vx_bnd  = (j_arr == 0) | (j_arr == n)
    Vx_vals = (j_arr == n).astype(float)
    Ax, bx  = _assemble(aP, aE, aN, aW, aS, bP, Vx_bnd, Vx_vals,
                         node, i_arr, j_arr, dim, N)

    # Vy: top row (i=0) → T=0 ; bottom row (i=n) → T=1
    Vy_bnd  = (i_arr == 0) | (i_arr == n)
    Vy_vals = (i_arr == n).astype(float)
    Ay, by  = _assemble(aP, aE, aN, aW, aS, bP, Vy_bnd, Vy_vals,
                         node, i_arr, j_arr, dim, N)

    X = spsolve(Ax, bx).reshape(dim, dim)
    Y = spsolve(Ay, by).reshape(dim, dim)

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


def _assemble(aP, aE, aN, aW, aS, bP, bnd, bc_vals, node, i_arr, j_arr, dim, N):
    """Build the CSR stiffness matrix and RHS for one diffusion solve.

    Boundary rows become identity rows (A[k,k]=1, b[k]=bc).
    Interior rows carry the 5-point stencil:
        aP·T - aE·T_east - aW·T_west - aS·T_south - aN·T_north = bP
    """
    interior = ~bnd
    aP_f = aP.ravel(); aE_f = aE.ravel(); aW_f = aW.ravel()
    aN_f = aN.ravel(); aS_f = aS.ravel(); bP_f = bP.ravel()

    # Main diagonal: 1 (boundary) or aP (interior)
    rs = [node];        cs = [node];        vs = [np.where(bnd, 1.0, aP_f)]

    # East  (j → j+1)
    m = interior & (j_arr + 1 < dim)
    rs.append(node[m]); cs.append(node[m] + 1);   vs.append(-aE_f[m])

    # West  (j → j-1)
    m = interior & (j_arr > 0)
    rs.append(node[m]); cs.append(node[m] - 1);   vs.append(-aW_f[m])

    # South (i → i+1)
    m = interior & (i_arr + 1 < dim)
    rs.append(node[m]); cs.append(node[m] + dim); vs.append(-aS_f[m])

    # North (i → i-1)
    m = interior & (i_arr > 0)
    rs.append(node[m]); cs.append(node[m] - dim); vs.append(-aN_f[m])

    A = csr_matrix(
        (np.concatenate(vs), (np.concatenate(rs), np.concatenate(cs))),
        shape=(N, N),
    )
    b = np.where(bnd, bc_vals, bP_f)
    return A, b


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
