"""
ERD Viewer - Databricks Unity Catalog ERD Viewer
Main Streamlit Application (Refactored & Modular)
"""
import streamlit as st
import os
from ui import (
    render_explorer_sidebar,
    render_erd_diagram
)

# Page configuration
st.set_page_config(
    page_title="ERD Viewer - Databricks Unity Catalog",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for compact styling
st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 1rem;
    }
    .table-details {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
    .column-detail {
        padding: 0.5rem;
        margin: 0.25rem 0;
        background-color: white;
        border-left: 3px solid #1f77b4;
    }
    .pk-indicator {
        background-color: #ffd700;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
        font-size: 0.8rem;
    }
    .fk-indicator {
        background-color: #87ceeb;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
        font-size: 0.8rem;
    }
    .not-null-indicator {
        background-color: #90ee90;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
        font-size: 0.8rem;
    }
    .stButton>button {
        width: 100%;
    }
    div[data-testid="stExpander"] {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'client' not in st.session_state:
        st.session_state.client = None
    if 'connected' not in st.session_state:
        st.session_state.connected = False
    if 'selected_catalog' not in st.session_state:
        st.session_state.selected_catalog = None
    if 'selected_schema' not in st.session_state:
        st.session_state.selected_schema = None
    if 'schema_metadata' not in st.session_state:
        st.session_state.schema_metadata = {}
    if 'selected_tables' not in st.session_state:
        st.session_state.selected_tables = []
    if 'minimized_tables' not in st.session_state:
        st.session_state.minimized_tables = set()
    if 'selected_table_detail' not in st.session_state:
        st.session_state.selected_table_detail = None
    if 'zoom_level' not in st.session_state:
        st.session_state.zoom_level = 100
    if 'highlight_column' not in st.session_state:
        st.session_state.highlight_column = None


def main():
    """Main application entry point"""
    initialize_session_state()
    
    # Render sidebar explorer
    render_explorer_sidebar()
    
    # Main content area
    if st.session_state.connected:
        # ERD Diagram with integrated search and table details panels
        render_erd_diagram()
    else:
        # Compact welcome screen
        st.markdown("## 📊 ERD Viewer")
        st.caption("View Entity Relationship Diagrams from Databricks Unity Catalog")
        
        st.markdown("""
        **🚀 Getting Started**
        1. Connect to Databricks (sidebar)
        2. Select catalog and schema
        3. View auto-generated ERD
        
        **✨ Features**
        - 🔍 Search tables/columns
        - 🔎 Zoom controls (embedded in diagram)
        - 📊 Interactive table details
        - 🔗 View FK/PK relationships
        
        **🔐 Connection**
        Use sidebar or set env vars:
        - `DATABRICKS_HOST`
        - `DATABRICKS_TOKEN`
        """)


if __name__ == "__main__":
    main()
