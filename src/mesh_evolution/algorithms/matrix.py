"""Matrix operations and solvers."""

import numpy as np
from typing import Tuple


class MatrixSolver:
    """Gaussian elimination solver with partial pivoting."""
    
    # Error codes
    NO_ERRORS = 0
    SINGULAR_MATRIX = 5
    NULL_PIVOT = 2
    NULL_PIVOT_SOLUTION = 3
    IMPOSSIBLE_REORDERING = 4
    
    @staticmethod
    def solve_gaussian_partial_pivot(
        A: np.ndarray,
        B: np.ndarray,
        debug: int = 0
    ) -> Tuple[np.ndarray, int]:
        """Solve Ax = B using Gaussian elimination with partial pivoting.
        
        Partial pivoting improves numerical stability by always selecting
        the row with the largest pivot element.
        
        Args:
            A: Coefficient matrix (n x n)
            B: Right-hand side vector (n,)
            debug: Debug level (0=none, >0=verbose)
            
        Returns:
            Tuple of (solution vector, error code)
            
        Raises:
            ValueError: If A is not square or dimensions don't match
        """
        A = A.copy().astype(float)
        B = B.copy().astype(float)
        
        if A.shape[0] != A.shape[1]:
            raise ValueError("A must be square")
        if A.shape[0] != len(B):
            raise ValueError("A and B dimensions don't match")
        
        n = len(B)
        Ipivot = np.arange(n)
        
        # Condensation phase (forward elimination)
        error = MatrixSolver._condense_with_pivot(A, B, Ipivot, debug)
        
        if error == 0:
            # Back substitution phase
            error = MatrixSolver._back_substitute(A, B, Ipivot, debug)
        
        return B, error
    
    @staticmethod
    def _condense_with_pivot(
        A: np.ndarray,
        B: np.ndarray,
        Ipivot: np.ndarray,
        debug: int
    ) -> int:
        """Condense matrix using partial pivoting.
        
        Args:
            A: Coefficient matrix (modified in-place)
            B: Right-hand side vector (modified in-place)
            Ipivot: Pivot index vector (modified in-place)
            debug: Debug level
            
        Returns:
            Error code
        """
        n = len(B)
        
        for i in range(n - 1):
            # Find row with maximum pivot element
            max_row = i
            for k in range(i + 1, n):
                if abs(A[Ipivot[k], i]) > abs(A[Ipivot[max_row], i]):
                    max_row = k
            
            # Swap rows
            Ipivot[i], Ipivot[max_row] = Ipivot[max_row], Ipivot[i]
            
            pivot = A[Ipivot[i], i]
            if abs(pivot) < 1e-14:
                return MatrixSolver.NULL_PIVOT
            
            # Eliminate column
            for k in range(i + 1, n):
                if abs(A[Ipivot[k], i]) > 1e-14:
                    factor = A[Ipivot[k], i] / pivot
                    A[Ipivot[k], i+1:] -= factor * A[Ipivot[i], i+1:]
                    B[Ipivot[k]] -= factor * B[Ipivot[i]]
                    A[Ipivot[k], i] = 0
        
        return MatrixSolver.NO_ERRORS
    
    @staticmethod
    def _back_substitute(
        A: np.ndarray,
        B: np.ndarray,
        Ipivot: np.ndarray,
        debug: int
    ) -> int:
        """Perform back substitution.
        
        Args:
            A: Upper triangular matrix from condensation
            B: Modified right-hand side vector
            Ipivot: Pivot index vector
            debug: Debug level
            
        Returns:
            Error code
        """
        n = len(B)
        X = np.zeros(n)
        
        for i in range(n - 1, -1, -1):
            row = Ipivot[i]
            X[i] = B[row]
            for j in range(i + 1, n):
                X[i] -= A[row, j] * X[j]
            
            if abs(A[row, i]) < 1e-14:
                return MatrixSolver.NULL_PIVOT_SOLUTION
            
            X[i] /= A[row, i]
        
        B[:] = X
        return MatrixSolver.NO_ERRORS


def mat2vec(matrix: np.ndarray) -> np.ndarray:
    """Convert matrix to vector (row-major order).
    
    Args:
        matrix: 2D numpy array
        
    Returns:
        1D numpy array (flattened matrix)
    """
    return matrix.flatten()


def vec2mat(vector: np.ndarray, n: int) -> np.ndarray:
    """Convert vector to n×n matrix.
    
    Args:
        vector: 1D numpy array with n*n elements
        n: Dimension of output matrix
        
    Returns:
        2D numpy array (n x n)
    """
    return vector.reshape((n, n))
