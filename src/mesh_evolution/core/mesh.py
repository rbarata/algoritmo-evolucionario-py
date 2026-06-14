"""Mesh deformation calculations."""

import numpy as np
from typing import Optional, Tuple

from .geometry import Point, Quadrilateral


class MeshCalculator:
    """Performs mesh deformation calculations."""
    
    @staticmethod
    def calculate_K_matrices(
        n: int,
        E: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate Kx and Ky from conductivity matrix E.
        
        The K matrices represent the stiffness of the mesh at each node.
        They are derived from the conductivity matrix E by averaging
        adjacent conductivity values.
        
        Args:
            n: Mesh dimension (n x n grid)
            E: Conductivity matrix (n x n)
            
        Returns:
            Kx, Ky matrices ((n+1) x (n+1))
            
        Raises:
            ValueError: If E is not n x n
        """
        if E.shape != (n, n):
            raise ValueError(f"E must be {n}x{n}, got {E.shape}")
        
        Kx = np.zeros((n + 1, n + 1))
        Ky = np.zeros((n + 1, n + 1))
        
        # Calculate Kx
        for i in range(n + 1):
            for j in range(n + 1):
                if j == n:
                    Kx[i, j] = 0
                elif i == 0:
                    Kx[i, j] = E[i, j]
                elif i == n:
                    Kx[i, j] = E[i - 1, j]
                else:
                    Kx[i, j] = (E[i - 1, j] + E[i, j]) / 2
        
        # Calculate Ky
        for i in range(n + 1):
            for j in range(n + 1):
                if i == n:
                    Ky[i, j] = 0
                elif j == 0:
                    Ky[i, j] = E[i, j]
                elif j == n:
                    Ky[i, j] = E[i, j - 1]
                else:
                    Ky[i, j] = (E[i, j - 1] + E[i, j]) / 2
        
        return Kx, Ky
    
    @staticmethod
    def calculate_coordinates(
        n: int,
        Kx: np.ndarray,
        Ky: np.ndarray,
        Vx: Optional[np.ndarray] = None,
        Vy: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate X and Y coordinates for mesh.
        
        Args:
            n: Mesh dimension
            Kx, Ky: K matrices (from calculate_K_matrices)
            Vx, Vy: Boundary conditions (optional)
            
        Returns:
            X, Y coordinate matrices ((n+1) x (n+1))
        """
        if Vx is None:
            Vx = np.zeros((n + 1, n + 1))
        if Vy is None:
            Vy = np.zeros((n + 1, n + 1))
        
        # Initialize boundary conditions
        for i in range(n + 1):
            Vx[i, 0] = 0
            Vx[i, n] = 1
            Vy[0, i] = 0
            Vy[n, i] = 1
        
        # Initialize coordinate matrices
        X = np.zeros((n + 1, n + 1))
        Y = np.zeros((n + 1, n + 1))
        
        for i in range(n + 1):
            for j in range(n + 1):
                X[i, j] = j / n
                Y[i, j] = i / n
        
        return X, Y
    
    @staticmethod
    def calculate_fitness(
        n: int,
        X: np.ndarray,
        Y: np.ndarray,
        E: np.ndarray,
        metric: str = 'sum'
    ) -> float:
        """Calculate fitness metric for mesh deformation.
        
        Args:
            n: Mesh dimension
            X, Y: Coordinate matrices
            E: Conductivity matrix
            metric: 'sum', 'deviation', 'std_deviation', or 'max'
            
        Returns:
            Fitness value (higher is better)
            
        Raises:
            ValueError: If metric is unknown
        """
        if metric == 'sum':
            return MeshCalculator._calculate_sum(n, X, Y, E)
        elif metric == 'deviation':
            return MeshCalculator._calculate_deviation(n, X, Y, E)
        elif metric == 'std_deviation':
            return MeshCalculator._calculate_std_deviation(n, X, Y, E)
        elif metric == 'max':
            return MeshCalculator._calculate_max(n, X, Y, E)
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
    @staticmethod
    def _calculate_sum(n: int, X: np.ndarray, Y: np.ndarray,
                       E: np.ndarray) -> float:
        """Calculate fitness as sum with penalty for negative areas."""
        soma = 0.0
        for i in range(n):
            for j in range(n):
                quad = Quadrilateral(
                    Point(X[i, j], Y[i, j]),
                    Point(X[i, j+1], Y[i, j+1]),
                    Point(X[i+1, j], Y[i+1, j]),
                    Point(X[i+1, j+1], Y[i+1, j+1])
                )
                prod = quad.area * E[i, j]
                if prod > 0:
                    soma += prod
                else:
                    soma += (-prod) * 1000
        return soma
    
    @staticmethod
    def _calculate_deviation(n: int, X: np.ndarray, Y: np.ndarray,
                            E: np.ndarray) -> float:
        """Calculate fitness as max-min difference."""
        max_val = -1.0
        min_val = 1e100
        
        for i in range(n):
            for j in range(n):
                quad = Quadrilateral(
                    Point(X[i, j], Y[i, j]),
                    Point(X[i, j+1], Y[i, j+1]),
                    Point(X[i+1, j], Y[i+1, j]),
                    Point(X[i+1, j+1], Y[i+1, j+1])
                )
                prod = quad.area * E[i, j]
                max_val = max(max_val, prod)
                min_val = min(min_val, prod)
        
        max_val *= n * n
        min_val *= n * n
        return max_val - min_val
    
    @staticmethod
    def _calculate_std_deviation(n: int, X: np.ndarray, Y: np.ndarray,
                                E: np.ndarray) -> float:
        """Calculate fitness as standard deviation."""
        areas = []
        for i in range(n):
            for j in range(n):
                quad = Quadrilateral(
                    Point(X[i, j], Y[i, j]),
                    Point(X[i, j+1], Y[i, j+1]),
                    Point(X[i+1, j], Y[i+1, j]),
                    Point(X[i+1, j+1], Y[i+1, j+1])
                )
                areas.append(quad.area * E[i, j])
        
        return float(np.std(areas))
    
    @staticmethod
    def _calculate_max(n: int, X: np.ndarray, Y: np.ndarray,
                      E: np.ndarray) -> float:
        """Calculate fitness as maximum area product."""
        max_val = -1.0
        for i in range(n):
            for j in range(n):
                quad = Quadrilateral(
                    Point(X[i, j], Y[i, j]),
                    Point(X[i, j+1], Y[i, j+1]),
                    Point(X[i+1, j], Y[i+1, j]),
                    Point(X[i+1, j+1], Y[i+1, j+1])
                )
                prod = quad.area * E[i, j]
                max_val = max(max_val, prod)
        
        return max_val * n * n
