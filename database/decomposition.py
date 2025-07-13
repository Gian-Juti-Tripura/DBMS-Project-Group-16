"""
Decomposition Checker Module

This module implements algorithms to check for lossless decomposition 
and dependency preservation in database normalization.
"""

import pandas as pd
from itertools import combinations, product
import numpy as np


class DecompositionChecker:
    """
    Checks for lossless decomposition and dependency preservation.
    """
    
    def __init__(self, original_data, functional_dependencies):
        """
        Initialize the decomposition checker.
        
        Args:
            original_data: pandas DataFrame containing the original dataset
            functional_dependencies: List of FDs as tuples (left_side, right_attr)
        """
        self.original_data = original_data
        self.attributes = list(original_data.columns)
        self.functional_dependencies = functional_dependencies
        
    def check_lossless_decomposition(self, relations):
        """
        Check if a decomposition is lossless using the chase test.
        
        Args:
            relations: List of relations, each containing 'attributes' and 'data'
            
        Returns:
            dict: Result containing lossless status and details
        """
        # Method 1: Chase Test
        chase_result = self._chase_test(relations)
        
        # Method 2: Natural Join Test (verification)
        join_result = self._natural_join_test(relations)
        
        return {
            'is_lossless': chase_result['is_lossless'],
            'method': 'Chase Test',
            'details': chase_result['details'],
            'verification': join_result
        }
    
    def _chase_test(self, relations):
        """
        Perform the chase test to check for lossless decomposition.
        
        Args:
            relations: List of relations
            
        Returns:
            dict: Chase test result
        """
        try:
            # Create chase tableau
            tableau = self._create_chase_tableau(relations)
            
            # Apply functional dependencies
            changed = True
            iterations = 0
            max_iterations = 100  # Prevent infinite loops
            
            while changed and iterations < max_iterations:
                changed = False
                iterations += 1
                
                for left_side, right_attr in self.functional_dependencies:
                    # Find rows with same values for left_side attributes
                    left_indices = [self.attributes.index(attr) for attr in left_side]
                    right_index = self.attributes.index(right_attr)
                    
                    # Group rows by left_side values
                    groups = {}
                    for i, row in enumerate(tableau):
                        left_key = tuple(row[j] for j in left_indices)
                        if left_key not in groups:
                            groups[left_key] = []
                        groups[left_key].append(i)
                    
                    # For each group, make right_attr values consistent
                    for group_rows in groups.values():
                        if len(group_rows) > 1:
                            # Find the "most specific" value (non-subscripted if exists)
                            right_values = [tableau[i][right_index] for i in group_rows]
                            target_value = self._find_most_specific_value(right_values)
                            
                            # Update all rows in group to have target_value
                            for row_idx in group_rows:
                                if tableau[row_idx][right_index] != target_value:
                                    tableau[row_idx][right_index] = target_value
                                    changed = True
            
            # Check if any row has all original values (no subscripts)
            for row in tableau:
                if all(not str(val).endswith(')') for val in row):
                    return {
                        'is_lossless': True,
                        'details': f'Chase test passed after {iterations} iterations'
                    }
            
            return {
                'is_lossless': False,
                'details': f'Chase test failed after {iterations} iterations'
            }
            
        except Exception as e:
            return {
                'is_lossless': False,
                'details': f'Chase test error: {str(e)}'
            }
    
    def _create_chase_tableau(self, relations):
        """
        Create the initial chase tableau.
        
        Args:
            relations: List of relations
            
        Returns:
            list: Chase tableau as list of lists
        """
        tableau = []
        
        for i, relation in enumerate(relations):
            row = []
            for attr in self.attributes:
                if attr in relation['attributes']:
                    row.append(attr)  # Original value
                else:
                    row.append(f"{attr}({i})")  # Subscripted value
            tableau.append(row)
        
        return tableau
    
    def _find_most_specific_value(self, values):
        """
        Find the most specific value (non-subscripted preferred).
        
        Args:
            values: List of values
            
        Returns:
            str: Most specific value
        """
        # Prefer non-subscripted values
        for val in values:
            if not str(val).endswith(')'):
                return val
        
        # If all are subscripted, return the first one
        return values[0]
    
    def _natural_join_test(self, relations):
        """
        Verify lossless decomposition by performing natural join.
        
        Args:
            relations: List of relations
            
        Returns:
            dict: Natural join test result
        """
        try:
            # Start with the first relation
            if not relations:
                return {'is_lossless': False, 'details': 'No relations provided'}
            
            result = relations[0]['data'].copy()
            
            # Perform natural join with each subsequent relation
            for i in range(1, len(relations)):
                relation_data = relations[i]['data']
                
                # Find common attributes
                common_attrs = list(set(result.columns) & set(relation_data.columns))
                
                if common_attrs:
                    # Perform natural join
                    result = result.merge(relation_data, on=common_attrs, how='inner')
                else:
                    # Cartesian product if no common attributes
                    result = result.assign(key=1).merge(
                        relation_data.assign(key=1), on='key'
                    ).drop('key', axis=1)
            
            # Check if result equals original data
            original_sorted = self.original_data.sort_values(by=self.attributes).reset_index(drop=True)
            result_sorted = result.sort_values(by=self.attributes).reset_index(drop=True)
            
            is_equal = original_sorted.equals(result_sorted)
            
            return {
                'is_lossless': is_equal,
                'details': f'Natural join {"preserves" if is_equal else "loses"} information',
                'original_tuples': len(original_sorted),
                'joined_tuples': len(result_sorted)
            }
            
        except Exception as e:
            return {
                'is_lossless': False,
                'details': f'Natural join test error: {str(e)}'
            }
    
    def check_dependency_preservation(self, relations):
        """
        Check if functional dependencies are preserved in the decomposition.
        
        Args:
            relations: List of relations
            
        Returns:
            dict: Dependency preservation result
        """
        preserved_fds = []
        lost_fds = []
        
        for left_side, right_attr in self.functional_dependencies:
            if self._is_fd_preserved(left_side, right_attr, relations):
                preserved_fds.append((left_side, right_attr))
            else:
                lost_fds.append((left_side, right_attr))
        
        preservation_rate = len(preserved_fds) / len(self.functional_dependencies) * 100
        
        return {
            'is_preserved': len(lost_fds) == 0,
            'preservation_rate': preservation_rate,
            'preserved_fds': preserved_fds,
            'lost_fds': lost_fds,
            'total_fds': len(self.functional_dependencies)
        }
    
    def _is_fd_preserved(self, left_side, right_attr, relations):
        """
        Check if a specific functional dependency is preserved.
        
        Args:
            left_side: Left side attributes of the FD
            right_attr: Right side attribute of the FD
            relations: List of relations
            
        Returns:
            bool: True if FD is preserved
        """
        # Check if the FD exists entirely within any single relation
        for relation in relations:
            if (set(left_side).issubset(set(relation['attributes'])) and 
                right_attr in relation['attributes']):
                return True
        
        # Check if FD can be derived from the decomposition
        # This is more complex and involves checking if the closure
        # of left_side includes right_attr using only FDs that are
        # preserved in individual relations
        
        return False
    
    def analyze_decomposition_quality(self, relations):
        """
        Provide a comprehensive analysis of decomposition quality.
        
        Args:
            relations: List of relations
            
        Returns:
            dict: Complete decomposition analysis
        """
        lossless_result = self.check_lossless_decomposition(relations)
        dependency_result = self.check_dependency_preservation(relations)
        
        # Calculate additional metrics
        total_attributes = len(self.attributes)
        total_relations = len(relations)
        avg_attributes_per_relation = sum(len(r['attributes']) for r in relations) / total_relations
        
        # Reduction in redundancy
        original_tuples = len(self.original_data)
        decomposed_tuples = sum(len(r['data']) for r in relations)
        redundancy_reduction = (1 - decomposed_tuples / (original_tuples * total_relations)) * 100
        
        # Quality score
        quality_score = self._calculate_quality_score(
            lossless_result['is_lossless'],
            dependency_result['preservation_rate'],
            redundancy_reduction
        )
        
        return {
            'lossless_decomposition': lossless_result,
            'dependency_preservation': dependency_result,
            'metrics': {
                'total_relations': total_relations,
                'avg_attributes_per_relation': round(avg_attributes_per_relation, 2),
                'redundancy_reduction': round(redundancy_reduction, 2),
                'quality_score': round(quality_score, 2)
            },
            'recommendation': self._generate_recommendation(
                lossless_result['is_lossless'],
                dependency_result['is_preserved'],
                quality_score
            )
        }
    
    def _calculate_quality_score(self, is_lossless, preservation_rate, redundancy_reduction):
        """
        Calculate overall quality score for decomposition.
        
        Args:
            is_lossless: Boolean indicating lossless decomposition
            preservation_rate: Percentage of preserved dependencies
            redundancy_reduction: Percentage of redundancy reduction
            
        Returns:
            float: Quality score (0-100)
        """
        lossless_score = 40 if is_lossless else 0
        dependency_score = (preservation_rate / 100) * 35
        redundancy_score = min(redundancy_reduction / 100, 1) * 25
        
        return lossless_score + dependency_score + redundancy_score
    
    def _generate_recommendation(self, is_lossless, is_preserved, quality_score):
        """
        Generate recommendation based on decomposition analysis.
        
        Args:
            is_lossless: Boolean indicating lossless decomposition
            is_preserved: Boolean indicating dependency preservation
            quality_score: Overall quality score
            
        Returns:
            str: Recommendation message
        """
        if is_lossless and is_preserved:
            return "Excellent decomposition! Both lossless and dependency-preserving."
        elif is_lossless and not is_preserved:
            return "Good decomposition with lossless join, but some dependencies are lost."
        elif not is_lossless and is_preserved:
            return "Dependencies are preserved but decomposition is lossy. Consider revision."
        else:
            return "Poor decomposition - both lossy and dependencies are lost. Revision needed."
    
    def get_decomposition_summary(self, relations):
        """
        Get a summary of decomposition analysis.
        
        Args:
            relations: List of relations
            
        Returns:
            dict: Comprehensive decomposition summary
        """
        analysis = self.analyze_decomposition_quality(relations)
        
        # Format relations summary
        relations_summary = []
        for i, relation in enumerate(relations):
            relations_summary.append({
                'name': relation.get('name', f'R{i+1}'),
                'attributes': relation['attributes'],
                'tuple_count': len(relation['data']),
                'primary_key': relation.get('primary_key', [])
            })
        
        return {
            'decomposition_analysis': analysis,
            'relations_summary': relations_summary,
            'total_original_tuples': len(self.original_data),
            'total_decomposed_tuples': sum(len(r['data']) for r in relations)
        }