"""
Normalization Engine Module

This module implements algorithms for database normalization including
1NF, 2NF, 3NF, and BCNF with dependency preservation and lossless decomposition.
"""

import pandas as pd
from itertools import combinations
from collections import defaultdict
import copy


class NormalizationEngine:
    """
    Handles database normalization from 1NF to BCNF.
    """
    
    def __init__(self, data, functional_dependencies, candidate_keys):
        """
        Initialize the normalization engine.
        
        Args:
            data: pandas DataFrame containing the dataset
            functional_dependencies: List of FDs as tuples (left_side, right_attr)
            candidate_keys: List of candidate keys
        """
        self.original_data = data
        self.attributes = list(data.columns)
        self.functional_dependencies = functional_dependencies
        self.candidate_keys = candidate_keys
        self.normalized_relations = []
        self.normalization_steps = []
        
    def check_normal_form(self, relation_attrs=None, fds=None):
        """
        Check what normal form the relation is in.
        
        Args:
            relation_attrs: List of attributes in the relation (default: all)
            fds: List of functional dependencies (default: all)
            
        Returns:
            str: Highest normal form achieved
        """
        if relation_attrs is None:
            relation_attrs = self.attributes
        if fds is None:
            fds = self.functional_dependencies
        
        # Check 1NF (assume data is already in 1NF)
        if not self._is_1nf():
            return "Not in 1NF"
        
        # Check 2NF
        if not self._is_2nf(relation_attrs, fds):
            return "1NF"
        
        # Check 3NF
        if not self._is_3nf(relation_attrs, fds):
            return "2NF"
        
        # Check BCNF
        if not self._is_bcnf(relation_attrs, fds):
            return "3NF"
        
        return "BCNF"
    
    def _is_1nf(self):
        """Check if the relation is in 1NF (atomic values)."""
        # For simplicity, assume data is already in 1NF
        return True
    
    def _is_2nf(self, relation_attrs, fds):
        """Check if the relation is in 2NF."""
        # Find candidate keys for this relation
        relation_candidate_keys = self._find_candidate_keys_for_relation(relation_attrs, fds)
        
        # Check for partial dependencies
        for left_side, right_attr in fds:
            if right_attr not in relation_attrs:
                continue
                
            # Check if left_side is a proper subset of any candidate key
            for candidate_key in relation_candidate_keys:
                if (set(left_side).issubset(set(candidate_key)) and 
                    set(left_side) != set(candidate_key) and
                    right_attr not in candidate_key):
                    return False
        
        return True
    
    def _is_3nf(self, relation_attrs, fds):
        """Check if the relation is in 3NF."""
        if not self._is_2nf(relation_attrs, fds):
            return False
        
        relation_candidate_keys = self._find_candidate_keys_for_relation(relation_attrs, fds)
        
        # Check for transitive dependencies
        for left_side, right_attr in fds:
            if right_attr not in relation_attrs:
                continue
                
            # Check if left_side is not a superkey and right_attr is not prime
            if not self._is_superkey(left_side, relation_attrs, fds):
                if not self._is_prime_attribute(right_attr, relation_candidate_keys):
                    return False
        
        return True
    
    def _is_bcnf(self, relation_attrs, fds):
        """Check if the relation is in BCNF."""
        # For every FD X -> Y, X must be a superkey
        for left_side, right_attr in fds:
            if right_attr not in relation_attrs:
                continue
                
            if not self._is_superkey(left_side, relation_attrs, fds):
                return False
        
        return True
    
    def _is_superkey(self, attributes, relation_attrs, fds):
        """Check if attributes form a superkey for the relation."""
        closure = self._compute_closure(attributes, fds)
        return set(relation_attrs).issubset(closure)
    
    def _is_prime_attribute(self, attribute, candidate_keys):
        """Check if an attribute is prime (part of any candidate key)."""
        for key in candidate_keys:
            if attribute in key:
                return True
        return False
    
    def _compute_closure(self, attributes, fds):
        """Compute closure of attributes given functional dependencies."""
        closure = set(attributes)
        changed = True
        
        while changed:
            changed = False
            for left_side, right_attr in fds:
                if set(left_side).issubset(closure) and right_attr not in closure:
                    closure.add(right_attr)
                    changed = True
        
        return closure
    
    def _find_candidate_keys_for_relation(self, relation_attrs, fds):
        """Find candidate keys for a specific relation."""
        candidate_keys = []
        
        for r in range(1, len(relation_attrs) + 1):
            for candidate in combinations(relation_attrs, r):
                if self._is_superkey(candidate, relation_attrs, fds):
                    # Check if it's minimal
                    is_minimal = True
                    for i in range(len(candidate)):
                        reduced = candidate[:i] + candidate[i+1:]
                        if reduced and self._is_superkey(reduced, relation_attrs, fds):
                            is_minimal = False
                            break
                    
                    if is_minimal:
                        candidate_keys.append(list(candidate))
        
        return candidate_keys
    
    def normalize_to_2nf(self):
        """Normalize the relation to 2NF."""
        if self._is_2nf(self.attributes, self.functional_dependencies):
            return [{'name': 'Original', 'attributes': self.attributes, 'data': self.original_data}]
        
        relations = []
        remaining_attrs = set(self.attributes)
        
        # Find partial dependencies
        for left_side, right_attr in self.functional_dependencies:
            for candidate_key in self.candidate_keys:
                if (set(left_side).issubset(set(candidate_key)) and 
                    set(left_side) != set(candidate_key)):
                    
                    # Create new relation for this partial dependency
                    new_relation_attrs = list(set(left_side + [right_attr]))
                    relations.append({
                        'name': f'R_{len(relations) + 1}',
                        'attributes': new_relation_attrs,
                        'data': self.original_data[new_relation_attrs].drop_duplicates()
                    })
                    remaining_attrs.discard(right_attr)
        
        # Create relation with remaining attributes
        if remaining_attrs:
            relations.append({
                'name': f'R_{len(relations) + 1}',
                'attributes': list(remaining_attrs),
                'data': self.original_data[list(remaining_attrs)].drop_duplicates()
            })
        
        return relations
    
    def normalize_to_3nf(self):
        """Normalize the relation to 3NF using synthesis algorithm."""
        # Step 1: Find minimal cover
        minimal_cover = self._find_minimal_cover()
        
        # Step 2: Create relations for each FD in minimal cover
        relations = []
        covered_attrs = set()
        
        for left_side, right_attr in minimal_cover:
            relation_attrs = list(set(left_side + [right_attr]))
            relations.append({
                'name': f'R_{len(relations) + 1}',
                'attributes': relation_attrs,
                'data': self.original_data[relation_attrs].drop_duplicates(),
                'primary_key': left_side
            })
            covered_attrs.update(relation_attrs)
        
        # Step 3: Add relation for candidate key if not covered
        uncovered_attrs = set(self.attributes) - covered_attrs
        if uncovered_attrs:
            # Find a candidate key that covers uncovered attributes
            for candidate_key in self.candidate_keys:
                if uncovered_attrs.issubset(set(candidate_key)):
                    relations.append({
                        'name': f'R_{len(relations) + 1}',
                        'attributes': candidate_key,
                        'data': self.original_data[candidate_key].drop_duplicates(),
                        'primary_key': candidate_key
                    })
                    break
        
        return relations
    
    def normalize_to_bcnf(self):
        """Normalize the relation to BCNF using decomposition algorithm."""
        relations = [{'name': 'Original', 'attributes': self.attributes, 'data': self.original_data}]
        
        while True:
            decomposed = False
            new_relations = []
            
            for relation in relations:
                attrs = relation['attributes']
                relevant_fds = self._get_relevant_fds(attrs)
                
                # Find a violating FD
                violating_fd = None
                for left_side, right_attr in relevant_fds:
                    if not self._is_superkey(left_side, attrs, relevant_fds):
                        violating_fd = (left_side, right_attr)
                        break
                
                if violating_fd:
                    # Decompose the relation
                    left_side, right_attr = violating_fd
                    
                    # R1: X ∪ Y
                    r1_attrs = list(set(left_side + [right_attr]))
                    r1_data = relation['data'][r1_attrs].drop_duplicates()
                    
                    # R2: X ∪ (R - Y)
                    r2_attrs = list(set(left_side + [attr for attr in attrs if attr != right_attr]))
                    r2_data = relation['data'][r2_attrs].drop_duplicates()
                    
                    new_relations.extend([
                        {'name': f"{relation['name']}_1", 'attributes': r1_attrs, 'data': r1_data},
                        {'name': f"{relation['name']}_2", 'attributes': r2_attrs, 'data': r2_data}
                    ])
                    decomposed = True
                else:
                    new_relations.append(relation)
            
            relations = new_relations
            if not decomposed:
                break
        
        return relations
    
    def _find_minimal_cover(self):
        """Find minimal cover of functional dependencies."""
        # Convert to canonical form (single attribute on right side)
        canonical_fds = []
        for left_side, right_attr in self.functional_dependencies:
            canonical_fds.append((left_side, right_attr))
        
        # Remove redundant FDs
        minimal_fds = []
        for fd in canonical_fds:
            # Check if this FD is redundant
            temp_fds = [f for f in canonical_fds if f != fd]
            if not self._is_fd_implied(fd, temp_fds):
                minimal_fds.append(fd)
        
        # Minimize left sides
        final_fds = []
        for left_side, right_attr in minimal_fds:
            minimal_left = self._minimize_left_side(left_side, right_attr, minimal_fds)
            final_fds.append((minimal_left, right_attr))
        
        return final_fds
    
    def _is_fd_implied(self, fd, fds):
        """Check if an FD is implied by a set of FDs."""
        left_side, right_attr = fd
        closure = self._compute_closure(left_side, fds)
        return right_attr in closure
    
    def _minimize_left_side(self, left_side, right_attr, fds):
        """Minimize the left side of an FD."""
        current_left = left_side[:]
        
        for attr in left_side:
            temp_left = [a for a in current_left if a != attr]
            if temp_left:
                # Check if reduced left side still implies right_attr
                temp_fds = [(l, r) for l, r in fds if not (l == left_side and r == right_attr)]
                temp_fds.append((temp_left, right_attr))
                
                if self._is_fd_implied((temp_left, right_attr), temp_fds):
                    current_left = temp_left
        
        return current_left
    
    def _get_relevant_fds(self, attributes):
        """Get functional dependencies relevant to a set of attributes."""
        relevant_fds = []
        for left_side, right_attr in self.functional_dependencies:
            if (set(left_side).issubset(set(attributes)) and 
                right_attr in attributes):
                relevant_fds.append((left_side, right_attr))
        return relevant_fds
    
    def suggest_optimal_normal_form(self):
        """Suggest the optimal normal form for the relation."""
        current_nf = self.check_normal_form()
        
        if current_nf == "BCNF":
            return "BCNF", "Already in BCNF - highest normal form"
        elif current_nf == "3NF":
            return "3NF", "Recommend 3NF - good balance between normalization and query performance"
        else:
            return "3NF", "Recommend normalizing to 3NF for better data integrity"
    
    def get_normalization_summary(self):
        """Get a comprehensive summary of normalization analysis."""
        current_nf = self.check_normal_form()
        optimal_nf, recommendation = self.suggest_optimal_normal_form()
        
        # Generate normalized relations for different normal forms
        relations_2nf = self.normalize_to_2nf() if current_nf in ["1NF", "Not in 1NF"] else []
        relations_3nf = self.normalize_to_3nf()
        relations_bcnf = self.normalize_to_bcnf()
        
        return {
            'current_normal_form': current_nf,
            'optimal_normal_form': optimal_nf,
            'recommendation': recommendation,
            'relations_2nf': relations_2nf,
            'relations_3nf': relations_3nf,
            'relations_bcnf': relations_bcnf,
            'total_relations_3nf': len(relations_3nf),
            'total_relations_bcnf': len(relations_bcnf)
        }