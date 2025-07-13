"""
Schema Generator Module

This module generates relational schemas and ER diagrams from normalized relations
with proper primary keys, foreign keys, and relationship mapping.
"""

import pandas as pd
import graphviz
from itertools import combinations
import json
import os


class SchemaGenerator:
    """
    Generates relational schemas and ER diagrams from normalized relations.
    """
    
    def __init__(self, normalized_relations, functional_dependencies, candidate_keys):
        """
        Initialize the schema generator.
        
        Args:
            normalized_relations: List of normalized relations
            functional_dependencies: List of functional dependencies
            candidate_keys: List of candidate keys from original relation
        """
        self.normalized_relations = normalized_relations
        self.functional_dependencies = functional_dependencies
        self.candidate_keys = candidate_keys
        self.relational_schema = {}
        self.er_components = {}
        
    def generate_relational_schema(self):
        """
        Generate relational schema with primary keys and foreign keys.
        
        Returns:
            dict: Complete relational schema
        """
        schema = {}
        
        for relation in self.normalized_relations:
            relation_name = relation['name']
            attributes = relation['attributes']
            
            # Determine primary key
            primary_key = self._determine_primary_key(relation)
            
            # Determine foreign keys
            foreign_keys = self._determine_foreign_keys(relation, schema)
            
            # Create attribute details
            attribute_details = self._create_attribute_details(attributes, primary_key, foreign_keys)
            
            schema[relation_name] = {
                'attributes': attribute_details,
                'primary_key': primary_key,
                'foreign_keys': foreign_keys,
                'tuple_count': len(relation['data']),
                'functional_dependencies': self._get_relevant_fds(attributes)
            }
        
        self.relational_schema = schema
        return schema
    
    def _determine_primary_key(self, relation):
        """
        Determine the primary key for a relation.
        
        Args:
            relation: Relation dictionary
            
        Returns:
            list: Primary key attributes
        """
        attributes = relation['attributes']
        
        # Check if primary key is explicitly provided
        if 'primary_key' in relation and relation['primary_key']:
            return relation['primary_key']
        
        # Find minimal superkey from candidate keys
        for candidate_key in self.candidate_keys:
            if set(candidate_key).issubset(set(attributes)):
                return candidate_key
        
        # Find functional dependencies that can form a key
        for left_side, right_attr in self.functional_dependencies:
            if (set(left_side).issubset(set(attributes)) and 
                right_attr in attributes):
                closure = self._compute_closure(left_side, attributes)
                if set(attributes).issubset(closure):
                    return left_side
        
        # Default to first attribute if no key found
        return [attributes[0]] if attributes else []
    
    def _determine_foreign_keys(self, relation, existing_schema):
        """
        Determine foreign keys for a relation.
        
        Args:
            relation: Current relation
            existing_schema: Already processed relations
            
        Returns:
            list: Foreign key specifications
        """
        foreign_keys = []
        relation_attrs = set(relation['attributes'])
        
        # Check for potential foreign keys in existing relations
        for schema_name, schema_info in existing_schema.items():
            other_primary_key = schema_info['primary_key']
            
            # Check if primary key of other relation is subset of current relation
            if (set(other_primary_key).issubset(relation_attrs) and 
                set(other_primary_key) != relation_attrs):
                
                foreign_keys.append({
                    'attributes': other_primary_key,
                    'references': {
                        'table': schema_name,
                        'attributes': other_primary_key
                    }
                })
        
        return foreign_keys
    
    def _create_attribute_details(self, attributes, primary_key, foreign_keys):
        """
        Create detailed attribute information.
        
        Args:
            attributes: List of attributes
            primary_key: Primary key attributes
            foreign_keys: Foreign key specifications
            
        Returns:
            dict: Detailed attribute information
        """
        attribute_details = {}
        
        # Get foreign key attributes
        fk_attrs = set()
        for fk in foreign_keys:
            fk_attrs.update(fk['attributes'])
        
        for attr in attributes:
            attribute_details[attr] = {
                'name': attr,
                'type': self._infer_data_type(attr),
                'is_primary_key': attr in primary_key,
                'is_foreign_key': attr in fk_attrs,
                'nullable': attr not in primary_key,
                'constraints': self._get_attribute_constraints(attr, primary_key, fk_attrs)
            }
        
        return attribute_details
    
    def _infer_data_type(self, attribute):
        """
        Infer data type for an attribute based on sample data.
        
        Args:
            attribute: Attribute name
            
        Returns:
            str: Inferred data type
        """
        # For demonstration, return generic types
        # In real implementation, analyze actual data
        common_types = {
            'id': 'INTEGER',
            'name': 'VARCHAR(100)',
            'email': 'VARCHAR(255)',
            'phone': 'VARCHAR(20)',
            'date': 'DATE',
            'price': 'DECIMAL(10,2)',
            'quantity': 'INTEGER'
        }
        
        attr_lower = attribute.lower()
        for keyword, data_type in common_types.items():
            if keyword in attr_lower:
                return data_type
        
        return 'VARCHAR(255)'  # Default type
    
    def _get_attribute_constraints(self, attribute, primary_key, foreign_key_attrs):
        """
        Get constraints for an attribute.
        
        Args:
            attribute: Attribute name
            primary_key: Primary key attributes
            foreign_key_attrs: Foreign key attributes
            
        Returns:
            list: List of constraints
        """
        constraints = []
        
        if attribute in primary_key:
            constraints.append('PRIMARY KEY')
            constraints.append('NOT NULL')
        
        if attribute in foreign_key_attrs:
            constraints.append('FOREIGN KEY')
        
        return constraints
    
    def _get_relevant_fds(self, attributes):
        """
        Get functional dependencies relevant to the relation.
        
        Args:
            attributes: Relation attributes
            
        Returns:
            list: Relevant functional dependencies
        """
        relevant_fds = []
        
        for left_side, right_attr in self.functional_dependencies:
            if (set(left_side).issubset(set(attributes)) and 
                right_attr in attributes):
                relevant_fds.append((left_side, right_attr))
        
        return relevant_fds
    
    def _compute_closure(self, attributes, relation_attrs):
        """
        Compute closure of attributes within a relation.
        
        Args:
            attributes: Starting attributes
            relation_attrs: Relation attributes
            
        Returns:
            set: Closure of attributes
        """
        closure = set(attributes)
        changed = True
        
        while changed:
            changed = False
            for left_side, right_attr in self.functional_dependencies:
                if (set(left_side).issubset(closure) and 
                    right_attr in relation_attrs and 
                    right_attr not in closure):
                    closure.add(right_attr)
                    changed = True
        
        return closure
    
    def generate_er_diagram(self, output_path='exports/er_diagram'):
        """
        Generate ER diagram from the relational schema.
        
        Args:
            output_path: Path to save the diagram
            
        Returns:
            dict: ER diagram information
        """
        if not self.relational_schema:
            self.generate_relational_schema()
        
        # Create entities
        entities = self._create_entities()
        
        # Create relationships
        relationships = self._create_relationships()
        
        # Generate diagram
        diagram_info = {
            'entities': entities,
            'relationships': relationships,
            'diagram_path': self._create_graphviz_diagram(entities, relationships, output_path)
        }
        
        self.er_components = diagram_info
        return diagram_info
    
    def _create_entities(self):
        """
        Create entities from relations.
        
        Returns:
            dict: Entity definitions
        """
        entities = {}
        
        for relation_name, relation_info in self.relational_schema.items():
            attributes = relation_info['attributes']
            primary_key = relation_info['primary_key']
            
            # Create entity
            entity_attributes = []
            for attr_name, attr_info in attributes.items():
                entity_attributes.append({
                    'name': attr_name,
                    'type': attr_info['type'],
                    'is_key': attr_info['is_primary_key'],
                    'is_derived': False,
                    'is_multivalued': False
                })
            
            entities[relation_name] = {
                'name': relation_name,
                'attributes': entity_attributes,
                'primary_key': primary_key,
                'entity_type': 'strong' if not relation_info['foreign_keys'] else 'weak'
            }
        
        return entities
    
    def _create_relationships(self):
        """
        Create relationships from foreign keys.
        
        Returns:
            dict: Relationship definitions
        """
        relationships = {}
        relationship_counter = 1
        
        for relation_name, relation_info in self.relational_schema.items():
            for fk in relation_info['foreign_keys']:
                referenced_table = fk['references']['table']
                
                relationship_name = f"R{relationship_counter}"
                relationships[relationship_name] = {
                    'name': relationship_name,
                    'entities': [referenced_table, relation_name],
                    'cardinality': self._determine_cardinality(referenced_table, relation_name),
                    'attributes': [],  # Most relationships don't have attributes
                    'type': 'identifying' if relation_info.get('entity_type') == 'weak' else 'non-identifying'
                }
                
                relationship_counter += 1
        
        return relationships
    
    def _determine_cardinality(self, entity1, entity2):
        """
        Determine cardinality between two entities.
        
        Args:
            entity1: First entity
            entity2: Second entity
            
        Returns:
            dict: Cardinality information
        """
        # For simplicity, assume one-to-many relationships
        # In real implementation, analyze data to determine actual cardinality
        return {
            entity1: 'one',
            entity2: 'many',
            'relationship_type': 'one-to-many'
        }
    
    def _create_graphviz_diagram(self, entities, relationships, output_path):
        """
        Create ER diagram using Graphviz.
        
        Args:
            entities: Entity definitions
            relationships: Relationship definitions
            output_path: Output file path
            
        Returns:
            str: Path to generated diagram
        """
        try:
            # Create Graphviz digraph
            dot = graphviz.Digraph(comment='ER Diagram', format='png')
            dot.attr(rankdir='TB', size='12,8')
            
            # Add entities
            for entity_name, entity_info in entities.items():
                # Create entity node
                label = f"<<TABLE BORDER='1' CELLBORDER='1' CELLSPACING='0'>"
                label += f"<TR><TD BGCOLOR='lightblue'><B>{entity_name}</B></TD></TR>"
                
                # Add attributes
                for attr in entity_info['attributes']:
                    attr_label = attr['name']
                    if attr['is_key']:
                        attr_label = f"<U>{attr_label}</U>"  # Underline key attributes
                    
                    label += f"<TR><TD>{attr_label}</TD></TR>"
                
                label += "</TABLE>>"
                
                dot.node(entity_name, label, shape='none')
            
            # Add relationships
            for rel_name, rel_info in relationships.items():
                # Create relationship node
                dot.node(rel_name, rel_name, shape='diamond', style='filled', fillcolor='lightgreen')
                
                # Connect entities to relationship
                for entity in rel_info['entities']:
                    cardinality = rel_info['cardinality'].get(entity, '1')
                    dot.edge(entity, rel_name, label=cardinality)
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Render the diagram
            dot.render(output_path, cleanup=True)
            
            return f"{output_path}.png"
            
        except Exception as e:
            print(f"Error creating ER diagram: {e}")
            return None
    
    def export_sql_schema(self, output_path='exports/schema.sql'):
        """
        Export relational schema as SQL DDL statements.
        
        Args:
            output_path: Path to save SQL file
            
        Returns:
            str: Path to generated SQL file
        """
        if not self.relational_schema:
            self.generate_relational_schema()
        
        sql_statements = []
        
        # Generate CREATE TABLE statements
        for table_name, table_info in self.relational_schema.items():
            sql = f"CREATE TABLE {table_name} (\n"
            
            # Add attributes
            attribute_definitions = []
            for attr_name, attr_info in table_info['attributes'].items():
                attr_def = f"    {attr_name} {attr_info['type']}"
                
                if not attr_info['nullable']:
                    attr_def += " NOT NULL"
                
                attribute_definitions.append(attr_def)
            
            sql += ",\n".join(attribute_definitions)
            
            # Add primary key constraint
            if table_info['primary_key']:
                pk_attrs = ", ".join(table_info['primary_key'])
                sql += f",\n    PRIMARY KEY ({pk_attrs})"
            
            # Add foreign key constraints
            for fk in table_info['foreign_keys']:
                fk_attrs = ", ".join(fk['attributes'])
                ref_table = fk['references']['table']
                ref_attrs = ", ".join(fk['references']['attributes'])
                sql += f",\n    FOREIGN KEY ({fk_attrs}) REFERENCES {ref_table}({ref_attrs})"
            
            sql += "\n);\n"
            sql_statements.append(sql)
        
        # Write to file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write("-- Generated Relational Schema\n")
            f.write("-- Database System Project-1: Normalization and ER Diagram Generator\n\n")
            f.write("\n".join(sql_statements))
        
        return output_path
    
    def get_schema_summary(self):
        """
        Get a comprehensive summary of the generated schema.
        
        Returns:
            dict: Schema summary
        """
        if not self.relational_schema:
            self.generate_relational_schema()
        
        total_relations = len(self.relational_schema)
        total_attributes = sum(len(info['attributes']) for info in self.relational_schema.values())
        total_foreign_keys = sum(len(info['foreign_keys']) for info in self.relational_schema.values())
        
        # Calculate normalization metrics
        avg_attributes_per_relation = total_attributes / total_relations if total_relations > 0 else 0
        
        return {
            'schema_statistics': {
                'total_relations': total_relations,
                'total_attributes': total_attributes,
                'total_foreign_keys': total_foreign_keys,
                'avg_attributes_per_relation': round(avg_attributes_per_relation, 2)
            },
            'relations': [
                {
                    'name': name,
                    'attributes': list(info['attributes'].keys()),
                    'primary_key': info['primary_key'],
                    'foreign_keys': len(info['foreign_keys']),
                    'tuple_count': info['tuple_count']
                }
                for name, info in self.relational_schema.items()
            ],
            'schema_quality': self._assess_schema_quality()
        }
    
    def _assess_schema_quality(self):
        """
        Assess the quality of the generated schema.
        
        Returns:
            dict: Quality assessment
        """
        total_relations = len(self.relational_schema)
        relations_with_pk = sum(1 for info in self.relational_schema.values() if info['primary_key'])
        relations_with_fk = sum(1 for info in self.relational_schema.values() if info['foreign_keys'])
        
        pk_coverage = (relations_with_pk / total_relations) * 100 if total_relations > 0 else 0
        referential_integrity = (relations_with_fk / max(total_relations - 1, 1)) * 100
        
        quality_score = (pk_coverage * 0.6) + (referential_integrity * 0.4)
        
        return {
            'primary_key_coverage': round(pk_coverage, 2),
            'referential_integrity': round(referential_integrity, 2),
            'quality_score': round(quality_score, 2),
            'assessment': self._get_quality_assessment(quality_score)
        }
    
    def _get_quality_assessment(self, score):
        """
        Get quality assessment based on score.
        
        Args:
            score: Quality score
            
        Returns:
            str: Quality assessment
        """
        if score >= 90:
            return "Excellent - Well-structured schema with proper keys and relationships"
        elif score >= 75:
            return "Good - Schema has most essential components"
        elif score >= 60:
            return "Fair - Schema needs improvement in key definitions"
        else:
            return "Poor - Schema requires significant improvements"