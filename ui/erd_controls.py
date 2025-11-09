"""
ERD Control Panel Module
Handles search inputs and filtering options
"""
import streamlit as st
from typing import Optional


def render_erd_controls():
    """Render compact ERD control panel"""
    if not st.session_state.schema_metadata:
        return
    
    # Compact search controls in columns
    col1, col2 = st.columns(2)
    with col1:
        table_search = st.text_input(
            "🔍 Search Tables",
            placeholder="Table name...",
            help="Shows matching tables + related tables (with FK relationships)",
            label_visibility="collapsed",
            key="table_search"
        )
    with col2:
        column_search = st.text_input(
            "🔍 Search Columns",
            placeholder="Column name...",
            help="Case-insensitive search",
            label_visibility="collapsed",
            key="column_search"
        )
    
    # Show info about table search including related tables
    if table_search:
        st.caption("💡 Showing matching tables + their related tables (FK relationships)")
    
    return table_search, column_search
