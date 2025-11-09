"""
ERD Diagram Rendering Module
"""
import streamlit as st
from typing import Optional
from erd_generator import CytoscapeERDGenerator
from .components import render_cytoscape


def render_erd_diagram():
    """Render the ERD diagram with integrated panels"""
    if not st.session_state.schema_metadata:
        st.info("👈 Please select a schema from the sidebar to generate ERD")
        return
    
    # Calculate relationship statistics
    total_fks = 0
    tables_with_fks = 0
    for table_name, table_info in st.session_state.schema_metadata.items():
        fk_count = len(table_info.get('foreign_keys', []))
        if fk_count > 0:
            total_fks += fk_count
            tables_with_fks += 1
    
    # Compact info bar with legend
    legend = "📖 Interactive ERD with integrated Search & Table Details | All panels are minimizable"
    if total_fks == 0:
        st.caption(f"⚠️ No FK relationships | {legend}")
    else:
        st.caption(f"🔗 {total_fks} relationship(s) | {legend}")
    
    # Generate Cytoscape diagram (no search filters, all handled in JS)
    cytoscape_elements = CytoscapeERDGenerator.generate_erd(
        schema_metadata=st.session_state.schema_metadata,
        selected_tables=st.session_state.selected_tables if st.session_state.selected_tables else None,
        minimized_tables=st.session_state.minimized_tables,
        search_table=None,
        search_column=None
    )
    
    # Render diagram with current zoom level and schema metadata for integrated panels
    render_cytoscape(
        cytoscape_elements, 
        st.session_state.zoom_level,
        st.session_state.schema_metadata
    )
