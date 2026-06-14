"""Geometric primitives for mesh calculations."""

import math
from dataclasses import dataclass


@dataclass
class Point:
    """2D point representation.
    
    Attributes:
        x: X coordinate
        y: Y coordinate
    """
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        """Calculate Euclidean distance to another point.
        
        Args:
            other: Another Point object
            
        Returns:
            Euclidean distance
        """
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def __repr__(self) -> str:
        return f"Point({self.x:.6f}, {self.y:.6f})"


@dataclass
class Quadrilateral:
    """4-point quadrilateral with area calculation.
    
    Attributes:
        p1: First point (usually bottom-left)
        p2: Second point (usually bottom-right)
        p3: Third point (usually top-left)
        p4: Fourth point (usually top-right)
    """
    p1: Point
    p2: Point
    p3: Point
    p4: Point
    
    @property
    def area(self) -> float:
        """Calculate quadrilateral area using shoelace formula.
        
        The shoelace formula calculates the area of a polygon given
        its vertices. For a quadrilateral with vertices in order,
        area = |sum of (x_i * y_i+1 - x_i+1 * y_i)| / 2
        
        Returns:
            Area of the quadrilateral
        """
        points = [self.p1, self.p2, self.p4, self.p3]
        n = len(points)
        area = 0.0
        
        for i in range(n):
            j = (i + 1) % n
            area += points[i].x * points[j].y
            area -= points[j].x * points[i].y
        
        return abs(area) / 2.0
    
    @property
    def perimeter(self) -> float:
        """Calculate quadrilateral perimeter.
        
        Returns:
            Perimeter of the quadrilateral
        """
        return (
            self.p1.distance_to(self.p2) +
            self.p2.distance_to(self.p4) +
            self.p4.distance_to(self.p3) +
            self.p3.distance_to(self.p1)
        )
    
    def is_valid(self) -> bool:
        """Check if quadrilateral is valid (positive area).
        
        Returns:
            True if area is positive, False otherwise
        """
        return self.area > 1e-14
    
    def __repr__(self) -> str:
        return f"Quadrilateral({self.p1}, {self.p2}, {self.p4}, {self.p3})"
