"""Numerical algorithms for mesh calculations."""

from .matrix import MatrixSolver, mat2vec, vec2mat
from .tdma import solve_tdma

__all__ = [
    "MatrixSolver",
    "mat2vec",
    "vec2mat",
    "solve_tdma",
]
