"""Numerical solver utilities and abstractions."""

import numpy as np
from typing import Protocol


class LinearSolver(Protocol):
    """Protocol for linear system solvers."""
    
    def solve(self, A: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Solve linear system Ax = b.
        
        Args:
            A: Coefficient matrix
            b: Right-hand side vector
            
        Returns:
            Solution vector x
        """
        ...
