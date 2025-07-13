"""
Functional Dependency Detection Module

This module implements algorithms to automatically detect functional dependencies
from given dataset using attribute closure and other heuristic methods.
"""

import pandas as pd
from itertools import combinations, chain
from collections import defaultdict
import numpy as np


class FunctionalDependencyDetector:
    """
    Detects functional dependencies from a dataset using various algorithms.
    """
    
    def __init__(self, data):
        """
        Initialize the FD detector with dataset.
        
        Args:
            data: pandas DataFrame containing the dataset
        """
        self.data = data
        self.attributes = list(data.columns)
        self.tuples = data.values.tolist()
        self.functional_dependencies = []
        self.candidate_keys = []
        
    def detect_functional_dependencies(self):
        """
        Main method to detect all functional dependencies in the dataset.
        
        Returns:
            list: List of functional dependencies as tuples (X, Y)
        """
        self.functional_dependencies = []
        
        # Check all possible combinations of attributes
        for r in range(1, len(self.attributes)):
            for left_side in combinations(self.attributes, r):
                remaining_attrs = [attr for attr in self.attributes if attr not in left_side]
                
                for right_attr in remaining_attrs:
                    if self._is_functional_dependency(left_side, right_attr):
                        self.functional_dependencies.append((list(left_side), right_attr))
        
        # Remove redundant FDs
        self.functional_dependencies = self._remove_redundant_fds(self.functional_dependencies)
        
        return self.functional_dependencies
    
    def _is_functional_dependency(self, left_side, right_attr):
        """
        Check if X -> Y is a functional dependency.
        
        Args:
            left_side: List of attributes on the left side
            right_attr: Single attribute on the right side
            
        Returns:
            bool: True if X -> Y is a functional dependency
        """
        # Group rows by left side attributes
        grouped = defaultdict(set)
        left_indices = [self.attributes.index(attr) for attr in left_side]
        right_index = self.attributes.index(right_attr)
        
        for row in self.tuples:
            left_key = tuple(row[i] for i in left_indices)
            right_value = row[right_index]
            grouped[left_key].add(right_value)
        
        # Check if each group has exactly one value for right side
        for values in grouped.values():
            if len(values) > 1:
                return False
        
        return True
    
    def _remove_redundant_fds(self, fds):
        """
        Remove redundant functional dependencies.
        
        Args:
            fds: List of functional dependencies
            
        Returns:
            list: List of minimal functional dependencies
        """
        minimal_fds = []
        
        for fd in fds:
            left_side, right_attr = fd
            
            # Check if this FD is minimal (not redundant)
            is_minimal = True
            for i in range(len(left_side)):
                reduced_left = left_side[:i] + left_side[i+1:]
                if reduced_left and self._is_functional_dependency(reduced_left, right_attr):
                    is_minimal = False
                    break
            
            if is_minimal:
                minimal_fds.append(fd)
        
        return minimal_fds
    
    def find_candidate_keys(self):
        """
        Find all candidate keys using the detected functional dependencies.
        
        Returns:
            list: List of candidate keys
        """
        self.candidate_keys = []
        
        # Generate all possible combinations of attributes
        for r in range(1, len(self.attributes) + 1):
            for candidate in combinations(self.attributes, r):
                if self._is_superkey(candidate):
                    # Check if it's minimal (candidate key)
                    is_minimal = True
                    for i in range(len(candidate)):
                        reduced_candidate = candidate[:i] + candidate[i+1:]
                        if reduced_candidate and self._is_superkey(reduced_candidate):
                            is_minimal = False
                            break
                    
                    if is_minimal:
                        self.candidate_keys.append(list(candidate))
        
        return self.candidate_keys
    
    def _is_superkey(self, attributes):
        """
        Check if a set of attributes forms a superkey.
        
        Args:
            attributes: List of attributes
            
        Returns:
            bool: True if attributes form a superkey
        """
        # A superkey uniquely identifies each tuple
        attr_indices = [self.attributes.index(attr) for attr in attributes]
        seen_combinations = set()
        
        for row in self.tuples:
            key_value = tuple(row[i] for i in attr_indices)
            if key_value in seen_combinations:
                return False
            seen_combinations.add(key_value)
        
        return True
    
    def attribute_closure(self, attributes, fds=None):
        """
        Compute the attribute closure for a given set of attributes.
        
        Args:
            attributes: Set of attributes
            fds: List of functional dependencies (uses detected FDs if None)
            
        Returns:
            set: Closure of the attributes
        """
        if fds is None:
            fds = self.functional_dependencies
        
        closure = set(attributes)
        changed = True
        
        while changed:
            changed = False
            for left_side, right_attr in fds:
                if set(left_side).issubset(closure) and right_attr not in closure:
                    closure.add(right_attr)
                    changed = True
        
        return closure
    
    def get_fd_summary(self):
        """
        Get a summary of detected functional dependencies.
        
        Returns:
            dict: Summary containing FDs, candidate keys, and statistics
        """
        if not self.functional_dependencies:
            self.detect_functional_dependencies()
        
        if not self.candidate_keys:
            self.find_candidate_keys()
        
        # Format FDs for display
        formatted_fds = []
        for left_side, right_attr in self.functional_dependencies:
            left_str = ", ".join(left_side)
            formatted_fds.append(f"{left_str} -> {right_attr}")
        
        return {
            'total_attributes': len(self.attributes),
            'total_tuples': len(self.tuples),
            'functional_dependencies': formatted_fds,
            'candidate_keys': self.candidate_keys,
            'total_fds': len(self.functional_dependencies),
            'total_candidate_keys': len(self.candidate_keys)
        }
    
    def export_fds_to_dict(self):
        """
        Export functional dependencies in a structured format.
        
        Returns:
            dict: Structured FD information
        """
        return {
            'attributes': self.attributes,
            'functional_dependencies': self.functional_dependencies,
            'candidate_keys': self.candidate_keys
        }