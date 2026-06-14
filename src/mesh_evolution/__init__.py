"""Mesh Evolution Algorithm - Python Implementation.

Evolutionary algorithm for optimizing mesh deformation based on conductivity
patterns and geometric constraints.
"""

__version__ = "2.0.0"
__author__ = "Rui Barata"
__all__ = [
    "EvolutionaryAlgorithm",
    "MeshCalculator",
    "Point",
    "Quadrilateral",
]

from .core.automato import EvolutionaryAlgorithm
from .core.geometry import Point, Quadrilateral
from .core.mesh import MeshCalculator
