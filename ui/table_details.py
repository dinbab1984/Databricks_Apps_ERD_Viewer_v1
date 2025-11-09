"""
Table Details Panel Module
"""
import streamlit as st
import pandas as pd
from typing import Optional


def render_table_details(column_search: Optional[str] = None, table_search: Optional[str] = None):
    """Render compact interactive table details panel at the bottom"""
    if not st.session_state.schema_metadata:
        return
    
    st.markdown("---")
    st.markdown("**📋 Table Details**")
    st.caption("💡 Showing only tables visible in ERD diagram")
    
    # Get tables that are currently visible in the ERD
    visible_tables = list(st.session_state.schema_metadata.keys())
    
    # Apply the same filters as the ERD diagram
    # 1. Apply selected_tables filter
    if st.session_state.selected_tables:
        visible_tables = [t for t in visible_tables if t in st.session_state.selected_tables]
    
    # 2. Apply table search filter (with related tables)
    if table_search:
        search_table_lower = table_search.lower()
        matching_tables = [
            t for t in visible_tables
            if search_table_lower in t.lower()
        ]
        
        # Add related tables (same logic as ERD generator)
        related_tables = set(matching_tables)
        for table_name in matching_tables:
            table_info = st.session_state.schema_metadata.get(table_name)
            if table_info:
                # Add parent tables
                for fk in table_info.get('foreign_keys', []):
                    parent_full_name = fk.get('parent_table', '')
                    if parent_full_name:
                        parent_table_name = parent_full_name.split('.')[-1]
                        if parent_table_name in visible_tables:
                            related_tables.add(parent_table_name)
                
                # Add child tables
                for other_table in visible_tables:
                    other_info = st.session_state.schema_metadata.get(other_table)
                    if other_info:
                        for fk in other_info.get('foreign_keys', []):
                            parent_full_name = fk.get('parent_table', '')
                            if parent_full_name:
                                parent_table_name = parent_full_name.split('.')[-1]
                                if parent_table_name == table_name:
                                    related_tables.add(other_table)
        
        visible_tables = list(related_tables)
    
    # 3. Apply column search filter
    if column_search:
        search_column_lower = column_search.lower()
        filtered_tables = []
        for table_name in visible_tables:
            table_info = st.session_state.schema_metadata.get(table_name)
            if table_info:
                for col in table_info['columns']:
                    if search_column_lower in col['name'].lower():
                        filtered_tables.append(table_name)
                        break
        visible_tables = filtered_tables
    
    all_tables = sorted(visible_tables)
    
    if not all_tables:
        st.info("No tables to display (check your filters)")
        return
    
    # Compact table selector
    selected_table = st.selectbox(
        "Select table:",
        options=all_tables,
        index=all_tables.index(st.session_state.selected_table_detail) 
              if st.session_state.selected_table_detail in all_tables else 0,
        label_visibility="collapsed"
    )
    
    st.session_state.selected_table_detail = selected_table
    
    if selected_table:
        table_info = st.session_state.schema_metadata[selected_table]
        
        # Compact table header
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(f"**📊 {selected_table}**")
        with col2:
            st.caption(f"📝 {len(table_info.get('columns', []))} cols")
        with col3:
            st.caption(f"📋 {table_info.get('table_type', 'TABLE')}")
        
        # Compact PK/FK info
        info_parts = []
        if table_info.get('primary_keys'):
            info_parts.append(f"🔑 PK: {', '.join(table_info['primary_keys'])}")
        if table_info.get('foreign_keys'):
            fk_count = len(table_info['foreign_keys'])
            info_parts.append(f"🔗 {fk_count} FK(s)")
        
        if info_parts:
            st.caption(" | ".join(info_parts))
        
        columns_data = []
        highlighted_columns = []
        
        for col in table_info.get('columns', []):
            # Build symbols matching ERD notation
            symbols = []
            if col['name'] in table_info.get('primary_keys', []):
                symbols.append('🔑')  # Key emoji for PK
            
            # Check if column is FK
            is_fk = False
            for fk in table_info.get('foreign_keys', []):
                if col['name'] in fk.get('child_columns', []):
                    is_fk = True
                    break
            if is_fk:
                symbols.append('🔗')  # Link emoji for FK
            
            if not col.get('nullable', True):
                symbols.append('⚠️')  # Warning emoji for NOT NULL
            
            # Format symbols as prefix (using emojis in table view for clarity)
            symbol_prefix = ''.join(symbols) + ' ' if symbols else ''
            
            # Check if column matches search
            is_highlighted = False
            if column_search and column_search.lower() in col['name'].lower():
                is_highlighted = True
                highlighted_columns.append(col['name'])
            
            # Format column name with symbol prefix
            column_name = f"{symbol_prefix}{col['name']}"
            if is_highlighted:
                column_name = f"🔍 {column_name}"
            
            columns_data.append({
                'Column': column_name,
                'Type': col['type'],
                'Nullable': '✓' if col.get('nullable', True) else '✗',
                'Comment': col.get('comment', '')
            })
        
        # Show search match info
        if column_search and highlighted_columns:
            st.info(f"🔍 Found {len(highlighted_columns)} matching column(s): {', '.join(highlighted_columns)}")
        elif column_search and not highlighted_columns:
            st.warning(f"⚠️ No columns matching '{column_search}' found in this table")
        
        # Display as table
        if columns_data:
            import pandas as pd
            df = pd.DataFrame(columns_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
