"""Tridiagonal Matrix Algorithm (TDMA) solver.

Also known as the Thomas Algorithm, solves tridiagonal systems
efficiently in O(n) time.
"""

import numpy as np


def solve_tdma(
    a_diag: np.ndarray,
    a_super: np.ndarray,
    a_sub: np.ndarray,
    b: np.ndarray
) -> np.ndarray:
    """Solve tridiagonal system using Thomas Algorithm.
    
    Solves the system:
        a_sub[i]*x[i-1] + a_diag[i]*x[i] + a_super[i]*x[i+1] = b[i]
    
    This is much more efficient than general Gaussian elimination for
    tridiagonal systems, running in O(n) instead of O(n^3).
    
    Args:
        a_diag: Main diagonal (size n)
        a_super: Super-diagonal/upper diagonal (size n-1)
        a_sub: Sub-diagonal/lower diagonal (size n-1)
        b: Right-hand side vector (size n)
        
    Returns:
        Solution vector x
        
    Raises:
        ValueError: If system is singular or dimensions don't match
    """
    n = len(b)
    
    if len(a_diag) != n:
        raise ValueError(f"Main diagonal must have {n} elements")
    if len(a_super) != n - 1:
        raise ValueError(f"Super-diagonal must have {n-1} elements")
    if len(a_sub) != n - 1:
        raise ValueError(f"Sub-diagonal must have {n-1} elements")
    
    # Make copies to avoid modifying input
    c_prime = np.zeros(n - 1)
    d_prime = np.zeros(n)
    
    # Forward sweep
    c_prime[0] = a_super[0] / a_diag[0]
    d_prime[0] = b[0] / a_diag[0]
    
    for i in range(1, n - 1):
        denom = a_diag[i] - a_sub[i-1] * c_prime[i-1]
        if abs(denom) < 1e-14:
            raise ValueError(f"Singular matrix at row {i}")
        c_prime[i] = a_super[i] / denom
        d_prime[i] = (b[i] - a_sub[i-1] * d_prime[i-1]) / denom
    
    denom = a_diag[n-1] - a_sub[n-2] * c_prime[n-2]
    if abs(denom) < 1e-14:
        raise ValueError(f"Singular matrix at row {n-1}")
    d_prime[n-1] = (b[n-1] - a_sub[n-2] * d_prime[n-2]) / denom
    
    # Back substitution
    x = np.zeros(n)
    x[n-1] = d_prime[n-1]
    for i in range(n - 2, -1, -1):
        x[i] = d_prime[i] - c_prime[i] * x[i+1]
    
    return x
