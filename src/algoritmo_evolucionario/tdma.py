import numpy as np


def calcular_tdma(T, aP, aE, aN, aW, aS, bP, boundary, VI_vals, dimensao, iteracoes, debug=0):
    """
    T         : (dim, dim) numpy array, modified in-place
    boundary  : (dim, dim) bool array — True where Dirichlet BC applies
    VI_vals   : (dim, dim) float array — Dirichlet values (0.0 where interior)

    Four-direction ADI sweep, Thomas algorithm vectorised over the perpendicular
    axis so each sweep is O(dim) Python iterations of O(dim) numpy vector ops
    rather than O(dim²) scalar Python iterations.
    """
    interior = ~boundary

    # Masked coefficient arrays — constant across iterations
    a    = np.where(interior, aP, 1.0)
    # W↔E sweeps: Thomas along axis-0 (rows k), coupling via aS (south=k+1) / aN (north=k-1)
    b_we = np.where(interior, aS, 0.0)
    c_we = np.where(interior, aN, 0.0)
    # N↔S sweeps: Thomas along axis-1 (cols k), coupling via aE (east=k+1) / aW (west=k-1)
    b_ns = np.where(interior, aE, 0.0)
    c_ns = np.where(interior, aW, 0.0)

    # Pre-allocate working arrays
    P      = np.empty_like(T)
    Q      = np.empty_like(T)
    T_prev = np.empty_like(T)
    T_next = np.empty_like(T)

    for _ in range(iteracoes):
        # ── W → E ──────────────────────────────────────────────────────────
        # Thomas along k (axis 0) for all columns simultaneously.
        # RHS couples to west (j-1) and east (j+1) neighbours.
        T_prev[:, 1:]  = T[:, :-1]; T_prev[:, 0]  = 0.0
        T_next[:, :-1] = T[:, 1:];  T_next[:, -1] = 0.0
        d = np.where(interior, aW * T_prev + aE * T_next + bP, VI_vals)
        _thomas_axis0(T, P, Q, a, b_we, c_we, d, dimensao)

        # ── N → S ──────────────────────────────────────────────────────────
        # Thomas along k (axis 1) for all rows simultaneously.
        # RHS couples to north (i-1) and south (i+1) neighbours.
        T_prev[1:, :]  = T[:-1, :]; T_prev[0, :]  = 0.0
        T_next[:-1, :] = T[1:, :];  T_next[-1, :] = 0.0
        d = np.where(interior, aN * T_prev + aS * T_next + bP, VI_vals)
        _thomas_axis1(T, P, Q, a, b_ns, c_ns, d, dimensao)

        # ── E → W ──────────────────────────────────────────────────────────
        T_prev[:, 1:]  = T[:, :-1]; T_prev[:, 0]  = 0.0
        T_next[:, :-1] = T[:, 1:];  T_next[:, -1] = 0.0
        d = np.where(interior, aW * T_prev + aE * T_next + bP, VI_vals)
        _thomas_axis0(T, P, Q, a, b_we, c_we, d, dimensao)

        # ── S → N ──────────────────────────────────────────────────────────
        T_prev[1:, :]  = T[:-1, :]; T_prev[0, :]  = 0.0
        T_next[:-1, :] = T[1:, :];  T_next[-1, :] = 0.0
        d = np.where(interior, aN * T_prev + aS * T_next + bP, VI_vals)
        _thomas_axis1(T, P, Q, a, b_ns, c_ns, d, dimensao)


def _thomas_axis0(T, P, Q, a, b, c, d, dim):
    """Thomas forward/back substitution along axis 0, vectorised over axis 1."""
    P[0] = b[0] / a[0]
    Q[0] = d[0] / a[0]
    for k in range(1, dim):
        denom  = a[k] - c[k] * P[k - 1]
        P[k]   = b[k] / denom
        Q[k]   = (d[k] + c[k] * Q[k - 1]) / denom
    T[dim - 1] = Q[dim - 1]
    for k in range(dim - 2, -1, -1):
        T[k] = P[k] * T[k + 1] + Q[k]


def _thomas_axis1(T, P, Q, a, b, c, d, dim):
    """Thomas forward/back substitution along axis 1, vectorised over axis 0."""
    P[:, 0] = b[:, 0] / a[:, 0]
    Q[:, 0] = d[:, 0] / a[:, 0]
    for k in range(1, dim):
        denom     = a[:, k] - c[:, k] * P[:, k - 1]
        P[:, k]   = b[:, k] / denom
        Q[:, k]   = (d[:, k] + c[:, k] * Q[:, k - 1]) / denom
    T[:, dim - 1] = Q[:, dim - 1]
    for k in range(dim - 2, -1, -1):
        T[:, k] = P[:, k] * T[:, k + 1] + Q[:, k]
