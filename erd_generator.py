"""
ERD Generator using Cytoscape.js
Generates Entity Relationship Diagrams from table metadata
"""
import json
import re
from typing import Dict, List, Set, Optional


class CytoscapeERDGenerator:
    """Generator for Cytoscape.js ERD diagrams"""
    
    @staticmethod
    def _sanitize_id(name: str) -> str:
        """
        Sanitize table/column names for use as IDs
        """
        # Replace special characters with underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = 'T_' + sanitized
        # Handle empty string
        if not sanitized:
            sanitized = 'TABLE'
        return sanitized
    
    @staticmethod
    def _format_column_display(
        col: Dict,
        primary_keys: List[str],
        foreign_key_columns: Set[str]
    ) -> str:
        """
        Format a column for display
        
        Returns a formatted string like: "🔑 user_id: bigint"
        """
        col_name = col['name']
        col_type = col['type']
        nullable = col.get('nullable', True)
        
        # Build constraint indicators
        indicators = []
        if col_name in primary_keys:
            indicators.append('🔑')
        if col_name in foreign_key_columns:
            indicators.append('🔗')
        if not nullable:
            indicators.append('⚠️')
        
        indicator_str = ' '.join(indicators) + ' ' if indicators else ''
        
        # Simplify complex types for display
        display_type = CytoscapeERDGenerator._simplify_type(col_type)
        
        return f"{indicator_str}{col_name}: {display_type}"
    
    @staticmethod
    def _simplify_type(type_name: str) -> str:
        """
        Simplify data type for display
        """
        if not type_name:
            return 'string'
        
        type_lower = type_name.lower()
        
        # Handle complex types
        if type_lower.startswith('struct'):
            return 'struct'
        if type_lower.startswith('array'):
            return 'array'
        if type_lower.startswith('map'):
            return 'map'
        if type_lower.startswith('decimal'):
            return 'decimal'
        if type_lower.startswith('varchar'):
            return 'varchar'
        if type_lower.startswith('char'):
            return 'char'
        
        # Return simplified type (limit length)
        return type_name[:20]
    
    @staticmethod
    def generate_erd(
        schema_metadata: Dict[str, Dict],
        selected_tables: Optional[List[str]] = None,
        minimized_tables: Optional[Set[str]] = None,
        search_table: Optional[str] = None,
        search_column: Optional[str] = None
    ) -> Dict:
        """
        Generate Cytoscape.js ERD diagram from schema metadata
        
        Args:
            schema_metadata: Dictionary of table metadata
            selected_tables: List of tables to include (None = all tables)
            minimized_tables: Set of table names to show in minimized view
            search_table: Table name search filter (case-insensitive contains)
            search_column: Column name search filter (case-insensitive contains)
            
        Returns:
            Dictionary with Cytoscape elements (nodes and edges)
        """
        minimized_tables = minimized_tables or set()
        
        # Filter tables based on selection
        tables_to_include = selected_tables if selected_tables else list(schema_metadata.keys())
        
        # Apply table search filter and include related tables
        if search_table:
            search_table_lower = search_table.lower()
            # Find directly matching tables
            matching_tables = [
                t for t in tables_to_include
                if search_table_lower in t.lower()
            ]
            
            # Find related tables (with FK relationships)
            related_tables = set(matching_tables)
            for table_name in matching_tables:
                table_info = schema_metadata.get(table_name)
                if table_info:
                    # Add parent tables
                    for fk in table_info.get('foreign_keys', []):
                        parent_full_name = fk.get('parent_table', '')
                        if parent_full_name:
                            parent_table_name = parent_full_name.split('.')[-1]
                            if parent_table_name in tables_to_include:
                                related_tables.add(parent_table_name)
                    
                    # Add child tables
                    for other_table in tables_to_include:
                        other_info = schema_metadata.get(other_table)
                        if other_info:
                            for fk in other_info.get('foreign_keys', []):
                                parent_full_name = fk.get('parent_table', '')
                                if parent_full_name:
                                    parent_table_name = parent_full_name.split('.')[-1]
                                    if parent_table_name == table_name:
                                        related_tables.add(other_table)
            
            tables_to_include = list(related_tables)
        
        # Apply column search filter
        if search_column:
            search_column_lower = search_column.lower()
            filtered_tables = []
            for table_name in tables_to_include:
                table_info = schema_metadata.get(table_name)
                if table_info:
                    for col in table_info['columns']:
                        if search_column_lower in col['name'].lower():
                            filtered_tables.append(table_name)
                            break
            tables_to_include = filtered_tables
        
        # Build Cytoscape elements
        nodes = []
        edges = []
        
        if not tables_to_include:
            # Return empty diagram with message
            return {
                'nodes': [{
                    'data': {
                        'id': 'no_tables',
                        'label': 'No tables found',
                        'type': 'message'
                    }
                }],
                'edges': []
            }
        
        # Create nodes (tables)
        for table_name in tables_to_include:
            table_info = schema_metadata.get(table_name)
            if not table_info:
                continue
            
            node_id = CytoscapeERDGenerator._sanitize_id(table_name)
            primary_keys = table_info.get('primary_keys', [])
            
            # Collect foreign key columns
            foreign_key_columns = set()
            for fk in table_info.get('foreign_keys', []):
                foreign_key_columns.update(fk.get('child_columns', []))
            
            # Format columns for display
            columns = table_info.get('columns', [])
            is_minimized = table_name in minimized_tables
            
            # Filter columns if column search is active
            if search_column:
                search_column_lower = search_column.lower()
                columns_to_show = []
                for col in columns:
                    if (search_column_lower in col['name'].lower() or
                        col['name'] in primary_keys or
                        col['name'] in foreign_key_columns):
                        columns_to_show.append(col)
                columns = columns_to_show
            
            # Limit columns if minimized
            if is_minimized and len(columns) > 5:
                # Show first 3 and last 2 columns, with ellipsis
                displayed_columns = columns[:3] + [{'name': '...', 'type': '', 'nullable': True}] + columns[-2:]
            else:
                displayed_columns = columns
            
            # Format column strings
            column_strings = []
            for col in displayed_columns:
                if col['name'] == '...':
                    column_strings.append('...')
                else:
                    col_str = CytoscapeERDGenerator._format_column_display(
                        col, primary_keys, foreign_key_columns
                    )
                    column_strings.append(col_str)
            
            # Determine if table has relationships
            has_fk = len(table_info.get('foreign_keys', [])) > 0
            is_referenced = False
            for other_table in tables_to_include:
                other_info = schema_metadata.get(other_table)
                if other_info:
                    for fk in other_info.get('foreign_keys', []):
                        parent_full_name = fk.get('parent_table', '')
                        if parent_full_name:
                            parent_table_name = parent_full_name.split('.')[-1]
                            if parent_table_name == table_name:
                                is_referenced = True
                                break
            
            # Create node
            node = {
                'data': {
                    'id': node_id,
                    'label': table_name,
                    'columns': column_strings,
                    'column_count': len(table_info.get('columns', [])),
                    'has_pk': len(primary_keys) > 0,
                    'has_fk': has_fk,
                    'is_referenced': is_referenced,
                    'is_minimized': is_minimized
                }
            }
            nodes.append(node)
        
        # Create edges (relationships)
        edge_id_counter = 0
        added_relationships = set()
        
        for table_name in tables_to_include:
            table_info = schema_metadata.get(table_name)
            if not table_info:
                continue
            
            child_id = CytoscapeERDGenerator._sanitize_id(table_name)
            foreign_keys = table_info.get('foreign_keys', [])
            
            for fk in foreign_keys:
                parent_full_name = fk.get('parent_table', '')
                child_columns = fk.get('child_columns', [])
                parent_columns = fk.get('parent_columns', [])
                
                if parent_full_name:
                    parent_table_name = parent_full_name.split('.')[-1]
                    
                    # Only add relationship if parent table is in diagram
                    if parent_table_name in tables_to_include:
                        parent_id = CytoscapeERDGenerator._sanitize_id(parent_table_name)
                        
                        # Build relationship label
                        child_col_str = ', '.join(child_columns) if child_columns else 'FK'
                        parent_col_str = ', '.join(parent_columns) if parent_columns else 'PK'
                        rel_label = f"{child_col_str} → {parent_col_str}"
                        
                        # Avoid duplicate relationships
                        rel_key = (parent_id, child_id, tuple(child_columns), tuple(parent_columns))
                        if rel_key not in added_relationships:
                            edge = {
                                'data': {
                                    'id': f'edge_{edge_id_counter}',
                                    'source': parent_id,
                                    'target': child_id,
                                    'label': rel_label,
                                    'child_columns': child_columns,
                                    'parent_columns': parent_columns
                                }
                            }
                            edges.append(edge)
                            added_relationships.add(rel_key)
                            edge_id_counter += 1
        
        print(f"DEBUG: Generated {len(nodes)} nodes and {len(edges)} edges")
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    @staticmethod
    def estimate_diagram_size(schema_metadata: Dict[str, Dict]) -> Dict[str, int]:
        """
        Estimate the size of the ERD diagram
        
        Returns:
            Dictionary with 'tables' and 'total_columns' counts
        """
        table_count = len(schema_metadata)
        total_columns = sum(
            len(table_info.get('columns', []))
            for table_info in schema_metadata.values()
        )
        
        return {
            'tables': table_count,
            'total_columns': total_columns,
            'avg_columns_per_table': total_columns / table_count if table_count > 0 else 0
        }
    
    @staticmethod
    def suggest_minimized_tables(
        schema_metadata: Dict[str, Dict],
        threshold_columns: int = 10
    ) -> Set[str]:
        """
        Suggest which tables should be minimized based on column count
        
        Args:
            schema_metadata: Dictionary of table metadata
            threshold_columns: Number of columns above which to suggest minimizing
            
        Returns:
            Set of table names to minimize
        """
        tables_to_minimize = set()
        
        for table_name, table_info in schema_metadata.items():
            column_count = len(table_info.get('columns', []))
            if column_count > threshold_columns:
                tables_to_minimize.add(table_name)
        
        return tables_to_minimize
