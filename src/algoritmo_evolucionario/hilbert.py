import math
import functools


def _xy2d(grid_n, x, y):
    """Hilbert curve index for (x, y) on a grid_n×grid_n grid (grid_n a power of 2)."""
    d = 0
    s = grid_n >> 1
    while s > 0:
        rx = 1 if (x & s) else 0
        ry = 1 if (y & s) else 0
        d += s * s * ((3 * rx) ^ ry)
        if ry == 0:
            if rx == 1:
                x = s - 1 - x
                y = s - 1 - y
            x, y = y, x
        s >>= 1
    return d


@functools.lru_cache(maxsize=8)
def hilbert_order(rows, cols):
    """Return (i, j) pairs for a rows×cols grid sorted by Hilbert curve index.

    Positions are ordered on a virtual 2^p × 2^p grid (the smallest that
    contains both dimensions), so physically close cells end up close in the
    returned sequence regardless of whether the grid is square or a power of 2.
    """
    p = max(1, math.ceil(math.log2(max(rows, cols))))
    grid_n = 1 << p
    positions = [(i, j) for i in range(rows) for j in range(cols)]
    return sorted(positions, key=lambda pos: _xy2d(grid_n, pos[0], pos[1]))
