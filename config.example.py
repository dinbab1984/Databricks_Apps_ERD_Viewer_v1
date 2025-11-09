"""
Configuration Example
Copy this file to config.py and update with your settings
"""

# Databricks Configuration
DATABRICKS_CONFIG = {
    # Your Databricks workspace URL
    'host': 'https://your-workspace.cloud.databricks.com',
    
    # Your Databricks personal access token
    # Get this from: User Settings > Access Tokens
    'token': 'your-access-token-here',
}

# Application Settings
APP_CONFIG = {
    # Default zoom level (50-200)
    'default_zoom': 100,
    
    # Threshold for auto-minimizing tables (number of columns)
    'auto_minimize_threshold': 10,
    
    # Maximum number of tables to display before prompting for selection
    'max_tables_warning': 20,
}

# UI Customization
UI_CONFIG = {
    # Page title
    'page_title': 'ERD Viewer - Databricks Unity Catalog',
    
    # Page icon (emoji)
    'page_icon': '📊',
    
    # Layout mode: 'wide' or 'centered'
    'layout': 'wide',
    
    # Sidebar state: 'expanded' or 'collapsed'
    'sidebar_state': 'expanded',
}

# Feature Flags
FEATURES = {
    # Enable table search
    'enable_table_search': True,
    
    # Enable column search
    'enable_column_search': True,
    
    # Enable zoom controls
    'enable_zoom': True,
    
    # Enable table selection
    'enable_table_selection': True,
    
    # Enable minimize/maximize
    'enable_minimize_maximize': True,
    
    # Enable table details panel
    'enable_table_details': True,
}

