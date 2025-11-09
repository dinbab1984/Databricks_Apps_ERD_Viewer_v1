# 🏗️ Architecture Documentation

## Overview

ERD Viewer is a Python web application built with Streamlit that generates and displays interactive Entity Relationship Diagrams from Databricks Unity Catalog schemas.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│                    (http://localhost:8501)                   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ HTTP
                             │
┌────────────────────────────▼────────────────────────────────┐
│                      Streamlit App                           │
│                        (app.py)                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  UI Components:                                        │ │
│  │  - Sidebar Explorer (Connection & Schema Selection)   │ │
│  │  - Main Panel (ERD Display & Controls)                │ │
│  │  - Details Panel (Table Information)                  │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────┬─────────────────────────┬────────────────────┘
               │                         │
               │ Python API              │ Python API
               │                         │
    ┌──────────▼──────────┐   ┌─────────▼──────────┐
    │  Databricks Client  │   │  ERD Generator     │
    │ (databricks_        │   │  (erd_generator.py)│
    │   client.py)        │   │                    │
    │                     │   │  - Mermaid syntax  │
    │  - List catalogs    │   │  - Diagram logic   │
    │  - List schemas     │   │  - Filtering       │
    │  - List tables      │   │  - Relationships   │
    │  - Get metadata     │   └────────────────────┘
    └──────────┬──────────┘
               │
               │ Databricks SDK
               │
    ┌──────────▼──────────────────────┐
    │   Databricks Unity Catalog      │
    │   (Remote - via REST API)       │
    └─────────────────────────────────┘
```

## Component Details

### 1. Frontend Layer (`app.py`)

**Responsibility**: User interface and user interaction handling

**Key Functions**:
- `initialize_session_state()`: Manages application state across user interactions
- `render_explorer_sidebar()`: Left sidebar for connection and schema selection
- `render_erd_controls()`: Control panel for search, zoom, and filters
- `render_erd_diagram()`: Main ERD visualization
- `render_table_details()`: Bottom panel for detailed table information
- `render_cytoscape()`: Renders interactive Cytoscape diagrams with multiple layouts

**Session State Variables**:
```python
{
    'client': DatabricksClient,  # Connection instance
    'connected': bool,                        # Connection status
    'selected_catalog': str,                  # Current catalog
    'selected_schema': str,                   # Current schema
    'schema_metadata': dict,                  # All table metadata
    'selected_tables': list,                  # Tables to display
    'minimized_tables': set,                  # Tables in minimized view
    'selected_table_detail': str,             # Table for details panel
    'zoom_level': int                         # Current zoom (50-200)
}
```

### 2. Data Access Layer (`databricks_client.py`)

**Responsibility**: Interface with Databricks Unity Catalog

**Class**: `DatabricksClient`

**Key Methods**:
- `list_catalogs()`: Retrieve all available catalogs
- `list_schemas(catalog_name)`: Get schemas in a catalog
- `list_tables(catalog_name, schema_name)`: Get tables in a schema
- `get_table_info(catalog, schema, table)`: Get detailed table metadata including:
  - Column names and types
  - Nullable constraints
  - Primary keys
  - Foreign keys with parent table references
- `get_schema_metadata(catalog, schema)`: Fetch metadata for entire schema

**Data Flow**:
```
User Selection → Client Method → Databricks SDK → Unity Catalog API → Response
```

### 3. Business Logic Layer (`erd_generator.py`)

**Responsibility**: Generate Cytoscape.js ERD diagrams from metadata

**Class**: `CytoscapeERDGenerator`

**Key Methods**:
- `generate_erd()`: Main generation method with filters
  - Parameters: metadata, selected_tables, minimized_tables, search filters
  - Returns: Dictionary with nodes and edges for Cytoscape
- `_format_column_display()`: Format individual columns with emoji indicators
- `_sanitize_id()`: Clean names for use as element IDs
- `estimate_diagram_size()`: Calculate diagram complexity
- `suggest_minimized_tables()`: Auto-optimization logic

**Cytoscape Output Format**:
```json
{
  "nodes": [
    {
      "data": {
        "id": "table_name",
        "label": "TableName",
        "columns": ["🔑 id: bigint", "name: varchar", ...],
        "has_pk": true,
        "has_fk": false
      }
    }
  ],
  "edges": [
    {
      "data": {
        "id": "edge_1",
        "source": "parent_table",
        "target": "child_table",
        "label": "child_col → parent_col"
      }
    }
  ]
}
```

## Data Flow

### 1. Connection Flow
```
User Input (Host, Token) 
  → connect_to_databricks()
  → DatabricksClient.__init__()
  → WorkspaceClient initialization
  → Session state update
  → UI refresh
```

### 2. Schema Loading Flow
```
User Selection (Catalog, Schema)
  → load_schema_metadata()
  → client.get_schema_metadata()
  → For each table:
      → client.get_table_info()
      → Extract columns, PK, FK
  → Store in session_state.schema_metadata
  → Auto-suggest minimized tables
  → UI refresh
```

### 3. ERD Generation Flow
```
Schema Metadata + User Filters
  → CytoscapeERDGenerator.generate_erd()
  → Apply table search filter
  → Apply column search filter
  → Build nodes (tables with columns)
  → Build edges (FK → PK relationships)
  → Return Cytoscape elements dict
  → render_cytoscape()
  → Browser renders via Cytoscape.js with interactive layout
```

### 4. Search/Filter Flow
```
User changes search/filter or layout
  → Session state update
  → generate_erd() with filters
  → Filtered diagram elements
  → render_cytoscape()
  → Cytoscape re-renders with new layout
  → UI update with smooth animation
```

## Key Design Decisions

### 1. Why Streamlit?
- **Rapid Development**: Python-native, no frontend code needed
- **State Management**: Built-in session state handling
- **Component Ecosystem**: Easy integration with visualization libraries
- **Data App Focus**: Perfect for data exploration tools

### 2. Why Cytoscape.js?
- **Interactive Graphs**: Purpose-built for network/graph visualization
- **Superior Performance**: Handles large schemas (100+ tables) efficiently
- **Rich Layouts**: Multiple automatic layout algorithms
- **Drag & Drop**: Native support for repositioning nodes
- **Browser Rendering**: No server-side image generation
- **Interactive**: Supports tooltips and interactions
- **ERD Support**: Native ER diagram type

### 3. Session State Pattern
All application state is stored in Streamlit's session state to:
- Persist data across reruns
- Avoid redundant API calls
- Maintain user selections and preferences

### 4. Lazy Loading
- Catalogs/schemas loaded on demand
- Table metadata fetched only when schema selected
- Reduces initial load time and API calls

### 5. Adaptive View
Auto-minimizes tables when:
- More than 10 tables in schema
- Total columns exceed 100
- Individual table has >10 columns

Provides optimal viewing experience for large schemas.

## Performance Considerations

### Caching
- Session state caches schema metadata
- No re-fetching unless user explicitly reloads

### Optimization for Large Schemas
- **Table Selection**: Display subset of tables
- **Search Filtering**: Reduce visible elements
- **Minimization**: Show only essential column info
- **Lazy Loading**: Fetch only selected schema

### Scalability Limits
- Tested up to 100 tables per schema
- Recommended: Use table selection for >50 tables
- Browser rendering may slow with >200 tables

## Security Model

### Authentication
- Databricks personal access token
- Token stored in session state (memory only)
- Optional environment variable configuration

### Authorization
- Inherits Unity Catalog permissions
- Read-only access required
- No write operations to catalog

### Data Handling
- No data persistence (except session state)
- No logging of sensitive information
- No external API calls (except Databricks)

## Error Handling

### Connection Errors
```python
try:
    client = DatabricksClient(host, token)
except Exception as e:
    st.error(f"Connection failed: {e}")
```

### API Errors
- Graceful degradation
- User-friendly error messages
- No application crashes

### Missing Data
- Empty states handled gracefully
- Default values provided
- Clear user guidance

## Extension Points

### 1. Add New Visualization
Implement additional diagram types by:
- Creating new generator class
- Adding toggle in UI
- Rendering alternative format

### 2. Export Functionality
Add export features:
- SVG/PNG export of diagrams
- PDF report generation
- SQL DDL generation

### 3. Additional Filters
Extend filtering:
- By table type (VIEW, TABLE, etc.)
- By column type
- By relationship patterns

### 4. Collaboration Features
- Share diagram links
- Save favorite schemas
- Export as Markdown

## Testing Strategy

### Unit Tests
- Test `DatabricksClient` methods
- Test `CytoscapeERDGenerator` logic
- Mock Databricks SDK responses

### Integration Tests
- Test end-to-end flows
- Verify Cytoscape element structure
- Test error scenarios

### Manual Testing
- Connection with various credentials
- Large schema performance
- UI responsiveness

## Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud
- Push to GitHub
- Connect repository
- Deploy with secrets management

### Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

### On-Premises
- Deploy on internal server
- Use enterprise authentication
- Integrate with SSO

## Future Enhancements

### Planned Features
1. **Export Options**: SVG, PNG, PDF export
2. **Diagram Layouts**: Multiple layout algorithms
3. **Collaboration**: Share and save diagrams
4. **History**: Track schema changes over time
5. **Comments**: Add notes to tables/columns
6. **Custom Themes**: Configurable color schemes
7. **Batch Mode**: Generate ERDs for multiple schemas
8. **API Mode**: REST API for diagram generation

### Technical Debt
1. Add comprehensive unit tests
2. Implement proper logging
3. Add configuration file support
4. Improve error messages
5. Add performance monitoring

---

**Last Updated**: October 2025
**Version**: 1.0.0

