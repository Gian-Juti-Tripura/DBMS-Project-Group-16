"""
Database System Project-1: Normalization and ER Diagram Generator
Database Module Package

This module contains all the core database functionality including:
- Functional Dependency Detection
- Normalization Algorithms
- Lossless Decomposition
- Schema Generation
"""

__version__ = "1.0.0"
__author__ = "MD Hasib Mia"

from .fd_detection import FunctionalDependencyDetector
from .normalization import NormalizationEngine
from .decomposition import DecompositionChecker
from .schema_generator import SchemaGenerator

__all__ = [
    'FunctionalDependencyDetector',
    'NormalizationEngine', 
    'DecompositionChecker',
    'SchemaGenerator'
]