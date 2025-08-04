"""
Functional Dependency Detection Module - Enhanced for Large Pharmaceutical Datasets

This module implements algorithms to automatically detect functional dependencies
from given dataset using attribute closure and other heuristic methods.
Optimized for large pharmaceutical datasets with complex multi-value patterns.
"""

import pandas as pd
from itertools import combinations, chain
from collections import defaultdict
import numpy as np
import time
from tqdm import tqdm


class FunctionalDependencyDetector:
    """
    Detects functional dependencies from a dataset using various algorithms.
    Enhanced for large pharmaceutical datasets.
    """
    
    def __init__(self, data, max_combinations=5, sample_size=None):
        """
        Initialize the FD detector with dataset.
        
        Args:
            data: pandas DataFrame containing the dataset
            max_combinations: Maximum number of attributes in left side of FD
            sample_size: Sample size for large datasets (None for all data)
        """
        # Use sampling for very large datasets
        if sample_size and len(data) > sample_size:
            self.data = data.sample(n=sample_size, random_state=42)
            self.is_sampled = True
            self.original_size = len(data)
        else:
            self.data = data
            self.is_sampled = False
            self.original_size = len(data)
            
        self.attributes = list(self.data.columns)
        self.tuples = self.data.values.tolist()
        self.functional_dependencies = []
        self.candidate_keys = []
        self.max_combinations = min(max_combinations, len(self.attributes) - 1)
        
        # Performance tracking
        self.detection_time = 0
        self.fds_checked = 0
        
    def detect_functional_dependencies(self):
        """
        Main method to detect all functional dependencies in the dataset.
        Enhanced with progress tracking and performance optimization.
        
        Returns:
            list: List of functional dependencies as tuples (X, Y)
        """
        print(f"Detecting functional dependencies on {len(self.data)} rows...")
        start_time = time.time()
        
        self.functional_dependencies = []
        self.fds_checked = 0
        
        # Pre-compute unique value counts for optimization
        unique_counts = {}
        for attr in self.attributes:
            unique_counts[attr] = self.data[attr].nunique()
        
        # Prioritize attributes with high uniqueness for potential keys
        sorted_attrs = sorted(self.attributes, key=lambda x: unique_counts[x], reverse=True)
        
        # Check all possible combinations of attributes with progress bar
        total_combinations = sum(len(list(combinations(self.attributes, r))) 
                               for r in range(1, self.max_combinations + 1))
        
        with tqdm(total=total_combinations, desc="Checking FDs") as pbar:
            for r in range(1, self.max_combinations + 1):
                for left_side in combinations(sorted_attrs, r):
                    remaining_attrs = [attr for attr in self.attributes if attr not in left_side]
                    
                    # Quick check: if left side doesn't have enough unique combinations,
                    # it can't determine many other attributes
                    left_combinations = self.data[list(left_side)].nunique()
                    if len(left_combinations) == 1:  # All same values
                        continue
                    
                    for right_attr in remaining_attrs:
                        self.fds_checked += 1
                        if self._is_functional_dependency_optimized(left_side, right_attr):
                            self.functional_dependencies.append((list(left_side), right_attr))
                    
                    pbar.update(1)
        
        # Remove redundant FDs
        self.functional_dependencies = self._remove_redundant_fds(self.functional_dependencies)
        
        self.detection_time = time.time() - start_time
        print(f"FD detection completed in {self.detection_time:.2f} seconds")
        print(f"Found {len(self.functional_dependencies)} functional dependencies")
        
        return self.functional_dependencies
    
    def _is_functional_dependency_optimized(self, left_attrs, right_attr):
        """
        Optimized check for functional dependency using pandas operations.
        
        Args:
            left_attrs: Left side attributes (determinant)
            right_attr: Right side attribute (dependent)
            
        Returns:
            bool: True if left_attrs -> right_attr is a functional dependency
        """
        # Group by left attributes and check if right attribute is unique in each group
        try:
            grouped = self.data.groupby(list(left_attrs))[right_attr].nunique()
            return all(count <= 1 for count in grouped)
        except Exception:
            # Fallback to original method for edge cases
            return self._is_functional_dependency(left_attrs, right_attr)
    
    def _is_functional_dependency(self, left_attrs, right_attr):
        """
        Check if left_attrs -> right_attr is a functional dependency.
        
        Args:
            left_attrs: Left side attributes (determinant)
            right_attr: Right side attribute (dependent)
            
        Returns:
            bool: True if it's a functional dependency
        """
        # Create a mapping from left side values to right side values
        left_to_right = {}
        
        for tuple_data in self.tuples:
            # Get values for left side attributes
            left_values = tuple([tuple_data[self.attributes.index(attr)] for attr in left_attrs])
            right_value = tuple_data[self.attributes.index(right_attr)]
            
            if left_values in left_to_right:
                if left_to_right[left_values] != right_value:
                    return False  # Violation found
            else:
                left_to_right[left_values] = right_value
        
        return True
    
    def _remove_redundant_fds(self, fds):
        """
        Remove redundant functional dependencies.
        Enhanced to handle pharmaceutical data patterns.
        
        Args:
            fds: List of functional dependencies
            
        Returns:
            list: Minimal set of functional dependencies
        """
        minimal_fds = []
        
        for fd in fds:
            left_side, right_attr = fd
            
            # Check if this FD is not implied by existing FDs
            if not self._is_implied_by_fds(left_side, right_attr, minimal_fds):
                minimal_fds.append(fd)
        
        # Additional optimization: remove FDs where left side can be reduced
        final_fds = []
        for left_side, right_attr in minimal_fds:
            minimal_left = self._find_minimal_left_side(left_side, right_attr)
            final_fds.append((minimal_left, right_attr))
        
        return final_fds
    
    def _find_minimal_left_side(self, left_side, right_attr):
        """
        Find the minimal left side for a functional dependency.
        
        Args:
            left_side: Current left side attributes
            right_attr: Right side attribute
            
        Returns:
            list: Minimal left side attributes
        """
        if len(left_side) == 1:
            return left_side
        
        # Try removing each attribute from left side
        for attr in left_side:
            reduced_left = [a for a in left_side if a != attr]
            if self._is_functional_dependency_optimized(reduced_left, right_attr):
                return self._find_minimal_left_side(reduced_left, right_attr)
        
        return left_side
    
    def _is_implied_by_fds(self, left_side, right_attr, existing_fds):
        """
        Check if a functional dependency is implied by existing FDs.
        
        Args:
            left_side: Left side attributes
            right_attr: Right side attribute
            existing_fds: List of existing functional dependencies
            
        Returns:
            bool: True if the FD is implied
        """
        # Use attribute closure to check if right_attr is in the closure of left_side
        closure = self._attribute_closure(left_side, existing_fds)
        return right_attr in closure
    
    def _attribute_closure(self, attributes, fds):
        """
        Compute attribute closure for a set of attributes.
        
        Args:
            attributes: Set of attributes
            fds: List of functional dependencies
            
        Returns:
            set: Closure of attributes
        """
        closure = set(attributes)
        changed = True
        
        while changed:
            changed = False
            for left_side, right_attr in fds:
                if set(left_side).issubset(closure) and right_attr not in closure:
                    closure.add(right_attr)
                    changed = True
        
        return closure
    
    def find_candidate_keys(self):
        """
        Find all candidate keys using the detected functional dependencies.
        Enhanced for pharmaceutical data patterns.
        
        Returns:
            list: List of candidate keys
        """
        print("Finding candidate keys...")
        self.candidate_keys = []
        
        # Start with single attributes that might be keys
        potential_keys = []
        
        # Check single attributes first
        for attr in self.attributes:
            if self.data[attr].nunique() == len(self.data):  # All unique values
                self.candidate_keys.append([attr])
                return self.candidate_keys  # Found a simple key
        
        # Check combinations of attributes
        for r in range(1, len(self.attributes)):
            for attr_combination in combinations(self.attributes, r):
                attr_list = list(attr_combination)
                
                # Check if this combination determines all other attributes
                closure = self._attribute_closure(attr_list, self.functional_dependencies)
                if len(closure) == len(self.attributes):
                    # This is a superkey, check if it's minimal
                    is_minimal = True
                    for existing_key in self.candidate_keys:
                        if set(existing_key).issubset(set(attr_list)):
                            is_minimal = False
                            break
                    
                    if is_minimal:
                        # Remove any existing keys that are supersets of this key
                        self.candidate_keys = [
                            key for key in self.candidate_keys 
                            if not set(attr_list).issubset(set(key))
                        ]
                        self.candidate_keys.append(attr_list)
            
            # If we found candidate keys, no need to check larger combinations
            if self.candidate_keys:
                break
        
        print(f"Found {len(self.candidate_keys)} candidate keys")
        return self.candidate_keys
    
    def get_fd_summary(self):
        """
        Get a summary of functional dependency analysis.
        Enhanced with pharmaceutical-specific insights.
        
        Returns:
            dict: Summary of FD analysis
        """
        summary = {
            'total_fds': len(self.functional_dependencies),
            'candidate_keys': self.candidate_keys,
            'detection_time': self.detection_time,
            'fds_checked': self.fds_checked,
            'dataset_info': {
                'rows': len(self.data),
                'original_rows': self.original_size,
                'columns': len(self.attributes),
                'is_sampled': self.is_sampled
            },
            'fd_details': []
        }
        
        # Categorize FDs by complexity
        simple_fds = []
        complex_fds = []
        
        for left_side, right_attr in self.functional_dependencies:
            fd_info = {
                'left_side': left_side,
                'right_attr': right_attr,
                'complexity': len(left_side),
                'left_side_str': ' + '.join(left_side),
                'fd_str': f"{' + '.join(left_side)} -> {right_attr}"
            }
            
            if len(left_side) == 1:
                simple_fds.append(fd_info)
            else:
                complex_fds.append(fd_info)
            
            summary['fd_details'].append(fd_info)
        
        summary['simple_fds'] = len(simple_fds)
        summary['complex_fds'] = len(complex_fds)
        
        # Add pharmaceutical-specific insights
        pharma_insights = self._get_pharmaceutical_insights()
        summary['pharmaceutical_insights'] = pharma_insights
        
        return summary
    
    def _get_pharmaceutical_insights(self):
        """
        Get insights specific to pharmaceutical data.
        
        Returns:
            dict: Pharmaceutical-specific insights
        """
        insights = {
            'drug_related_fds': [],
            'clinical_trial_fds': [],
            'company_related_fds': [],
            'side_effect_patterns': []
        }
        
        # Identify pharmaceutical-related FDs
        for left_side, right_attr in self.functional_dependencies:
            left_str = ' + '.join(left_side).lower()
            right_str = right_attr.lower()
            
            # Drug-related FDs
            if any(term in left_str for term in ['drug', 'medication', 'product']):
                insights['drug_related_fds'].append({
                    'left_side': left_side,
                    'right_attr': right_attr,
                    'fd_str': f"{' + '.join(left_side)} -> {right_attr}"
                })
            
            # Clinical trial FDs
            if any(term in left_str or term in right_str for term in ['trial', 'clinical', 'study']):
                insights['clinical_trial_fds'].append({
                    'left_side': left_side,
                    'right_attr': right_attr,
                    'fd_str': f"{' + '.join(left_side)} -> {right_attr}"
                })
            
            # Company-related FDs
            if any(term in left_str or term in right_str for term in ['company', 'manufacturer']):
                insights['company_related_fds'].append({
                    'left_side': left_side,
                    'right_attr': right_attr,
                    'fd_str': f"{' + '.join(left_side)} -> {right_attr}"
                })
            
            # Side effect patterns
            if 'side effect' in left_str or 'side effect' in right_str:
                insights['side_effect_patterns'].append({
                    'left_side': left_side,
                    'right_attr': right_attr,
                    'fd_str': f"{' + '.join(left_side)} -> {right_attr}"
                })
        
        return insights