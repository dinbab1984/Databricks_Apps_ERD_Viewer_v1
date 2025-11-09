"""
Sidebar Explorer UI Module
Handles catalog/schema navigation and connection
"""
import os
from typing import Optional
import streamlit as st
from databricks_client import DatabricksClient
from erd_generator import CytoscapeERDGenerator

def connect_to_databricks(
    host: Optional[str] = None,
    token: Optional[str] = None,
    profile: Optional[str] = None,
):
    """Connect to Databricks (works in Databricks Apps and locally)."""
    try:
        # In Databricks Apps with user authorization enabled, the user's token
        # is forwarded in this header and will be used automatically.
        headers = None
        if hasattr(st, "context") and st.context:
            try:
                headers = st.context.headers
                print(f"DEBUG SIDEBAR: st.context.headers captured, type={type(headers)}")
                
                # Try to list available headers for debugging
                if hasattr(headers, 'keys'):
                    header_keys = list(headers.keys())
                    print(f"DEBUG SIDEBAR: Total headers available: {len(header_keys)}")
                    
                    # Check for OAuth-specific headers
                    oauth_headers = [k for k in header_keys if 'token' in k.lower() or 'auth' in k.lower()]
                    print(f"DEBUG SIDEBAR: OAuth/Auth related headers: {oauth_headers}")
                    
                    # Check for Cookie header (might contain OAuth session)
                    cookie_headers = [k for k in header_keys if 'cookie' in k.lower()]
                    if cookie_headers:
                        print(f"DEBUG SIDEBAR: Cookie headers found: {cookie_headers}")
                        for key in cookie_headers:
                            try:
                                value = headers[key]
                                # Look for OAuth-related cookies
                                if value and ('oauth' in str(value).lower() or 'token' in str(value).lower()):
                                    print(f"DEBUG SIDEBAR: {key} contains OAuth-related cookies")
                            except:
                                pass
                    
                    # Print ALL header values (first 100 chars) for OAuth headers
                    for key in oauth_headers:
                        try:
                            value = headers[key]
                            if value:
                                print(f"DEBUG SIDEBAR: {key} = {str(value)[:100]}...")
                        except:
                            pass
                    
                    # Also check for X-Forwarded-User (should show actual email if OAuth working)
                    user_email_headers = ['X-Forwarded-Email', 'X-Forwarded-User', 'X-Forwarded-Preferred-Username']
                    for key in user_email_headers:
                        if key in header_keys:
                            try:
                                value = headers[key]
                                print(f"DEBUG SIDEBAR: {key} = {value}")
                            except:
                                pass
                            
                elif hasattr(headers, '__dict__'):
                    print(f"DEBUG SIDEBAR: Available header attributes: {list(headers.__dict__.keys())}")
            except Exception as e:
                print(f"DEBUG SIDEBAR: Error capturing headers: {e}")
                headers = None
        else:
            print("DEBUG SIDEBAR: st.context not available")

        print(f"DEBUG SIDEBAR: Passing headers to DatabricksClient: {headers is not None}")
        
        st.session_state.client = DatabricksClient(
            host=host,
            token=token,
            request_headers=headers,  # enables OBO when available
            profile=profile,          # local CLI profile fallback
        )
        st.session_state.connected = True
        st.success("✅ Connected successfully!")
    except Exception as e:
        st.session_state.connected = False
        st.error(f"Failed to connect to Databricks: {str(e)}")


def load_schema_metadata(catalog: str, schema: str):
    """Load metadata for selected schema"""
    if st.session_state.client:
        with st.spinner(f"Loading metadata for {catalog}.{schema}..."):
            st.session_state.schema_metadata = st.session_state.client.get_schema_metadata(catalog, schema)
            st.session_state.selected_catalog = catalog
            st.session_state.selected_schema = schema
            st.session_state.selected_tables = list(st.session_state.schema_metadata.keys())
            
            erd_size = CytoscapeERDGenerator.estimate_diagram_size(st.session_state.schema_metadata)
            if erd_size['tables'] > 10 or erd_size['total_columns'] > 100:
                st.session_state.minimized_tables = CytoscapeERDGenerator.suggest_minimized_tables(st.session_state.schema_metadata)
            else:
                st.session_state.minimized_tables = set()


def render_explorer_sidebar():
    """Render compact left sidebar explorer"""
    with st.sidebar:
        st.markdown("**📊 ERD Viewer**")
        st.caption("Databricks Unity Catalog")
        
        # Auto-connect if running in Databricks Apps (OBO) or with env credentials
        if not st.session_state.connected and 'auto_connect_attempted' not in st.session_state:
            st.session_state.auto_connect_attempted = True
            
            # Check if running in Databricks Apps with OBO
            is_databricks_app = False
            if hasattr(st, "context") and st.context:
                try:
                    headers = st.context.headers
                    # Check for OBO token or other Databricks App indicators
                    if hasattr(headers, 'get'):
                        is_databricks_app = headers.get("x-forwarded-access-token") is not None
                    else:
                        is_databricks_app = getattr(headers, "x-forwarded-access-token", None) is not None
                except Exception:
                    pass
            
            auto_host = os.getenv('DATABRICKS_HOST', '')
            auto_token = os.getenv('DATABRICKS_TOKEN', '')
            
            # Auto-connect if: OBO is available OR env vars are set
            if is_databricks_app or (auto_host and auto_token):
                with st.spinner("🔄 Auto-connecting to workspace..."):
                    if is_databricks_app:
                        # OBO mode: SDK will auto-discover host and use forwarded token
                        connect_to_databricks(host=None, token=None)
                        if st.session_state.connected:
                            st.success("✅ Auto-connected using OBO (running as your user)!")
                            st.rerun()
                    else:
                        # Env var mode
                        connect_to_databricks(auto_host, auto_token)
                        if st.session_state.connected:
                            st.success("✅ Auto-connected using workspace credentials!")
                            st.rerun()
        
        # Connection settings
        with st.expander("🔌 Connect", expanded=not st.session_state.connected):
            # Check if running in Databricks Apps
            in_databricks_app = hasattr(st, "context") and st.context
            
            if not st.session_state.connected:
                if in_databricks_app:
                    st.info("ℹ️ **Databricks Apps Mode**\nClick Connect to authenticate with your credentials (OBO).")
                elif os.getenv('DATABRICKS_HOST') and os.getenv('DATABRICKS_TOKEN'):
                    st.success("✓ **Environment Variables Detected**\nReady to connect using DATABRICKS_HOST and DATABRICKS_TOKEN.")
                else:
                    st.warning("⚠️ **Missing Credentials**\nSet DATABRICKS_HOST and DATABRICKS_TOKEN environment variables.")
                    st.caption("For local dev: Export env vars before running the app.")
            
            # Simple connect button - no manual input fields
            if st.button("Connect", type="primary", key="connect_button", use_container_width=True):
                connect_to_databricks(host=None, token=None)
        
        if not st.session_state.connected:
            st.caption("👆 Connect to get started")
            return
        
        st.caption("✅ Connected")
        
        # Catalog and Schema selection
        st.markdown("**📂 Schema**")
        
        try:
            catalogs = st.session_state.client.list_catalogs()
            
            if catalogs:
                selected_catalog = st.selectbox(
                    "Catalog",
                    options=catalogs,
                    index=catalogs.index(st.session_state.selected_catalog) 
                          if st.session_state.selected_catalog in catalogs else 0,
                    key="catalog_selector",
                    label_visibility="collapsed"
                )
                
                if selected_catalog:
                    schemas = st.session_state.client.list_schemas(selected_catalog)
                    
                    if schemas:
                        selected_schema = st.selectbox(
                            "Schema",
                            options=schemas,
                            index=schemas.index(st.session_state.selected_schema)
                                  if st.session_state.selected_schema in schemas else 0,
                            key="schema_selector",
                            label_visibility="collapsed"
                        )
                        
                        if st.button("Load", type="primary", key="load_schema_button", use_container_width=True):
                            load_schema_metadata(selected_catalog, selected_schema)
                    else:
                        st.caption("⚠️ No schemas")
            else:
                st.caption("⚠️ No catalogs")
        except Exception as e:
            st.caption(f"❌ Error: {str(e)[:50]}")
        
        # Display current schema info
        if st.session_state.selected_schema:
            st.caption(f"📊 {st.session_state.selected_catalog}.{st.session_state.selected_schema}")
            
            if st.session_state.schema_metadata:
                erd_size = CytoscapeERDGenerator.estimate_diagram_size(st.session_state.schema_metadata)
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"📋 {erd_size['tables']} tables")
                with col2:
                    st.caption(f"📝 {erd_size['total_columns']} cols")
                
                # Table selection tree view
                st.markdown("**🗂️ Select Tables**")
                
                # Get all tables
                all_tables = sorted(st.session_state.schema_metadata.keys())
                
                # Selection mode toggle
                select_mode = st.radio(
                    "Mode",
                    ["All Tables", "Select Specific"],
                    horizontal=True,
                    label_visibility="collapsed",
                    key="table_select_mode"
                )
                
                if select_mode == "All Tables":
                    st.session_state.selected_tables = None
                    st.caption(f"✅ Showing all {len(all_tables)} tables")
                else:
                    # Multi-select for tables
                    selected_tables = st.multiselect(
                        "Choose tables",
                        options=all_tables,
                        default=st.session_state.selected_tables if st.session_state.selected_tables else [],
                        placeholder="Select tables...",
                        label_visibility="collapsed",
                        key="table_multiselect"
                    )
                    
                    if selected_tables:
                        st.session_state.selected_tables = selected_tables
                        st.caption(f"✅ Selected {len(selected_tables)} table(s)")
                        
                        # Option to include related tables
                        if st.checkbox("➕ Include related tables", value=False, key="include_related"):
                            # Find related tables
                            related_tables = set(selected_tables)
                            for table_name in selected_tables:
                                table_info = st.session_state.schema_metadata.get(table_name)
                                if table_info:
                                    # Add parent tables
                                    for fk in table_info.get('foreign_keys', []):
                                        parent_full_name = fk.get('parent_table', '')
                                        if parent_full_name:
                                            parent_table_name = parent_full_name.split('.')[-1]
                                            if parent_table_name in all_tables:
                                                related_tables.add(parent_table_name)
                                    
                                    # Add child tables
                                    for other_table in all_tables:
                                        other_info = st.session_state.schema_metadata.get(other_table)
                                        if other_info:
                                            for fk in other_info.get('foreign_keys', []):
                                                parent_full_name = fk.get('parent_table', '')
                                                if parent_full_name:
                                                    parent_table_name = parent_full_name.split('.')[-1]
                                                    if parent_table_name == table_name:
                                                        related_tables.add(other_table)
                            
                            st.session_state.selected_tables = list(related_tables)
                            added_count = len(related_tables) - len(selected_tables)
                            if added_count > 0:
                                st.caption(f"➕ Added {added_count} related table(s)")
                    else:
                        st.session_state.selected_tables = []
                        st.caption("⚠️ No tables selected")
