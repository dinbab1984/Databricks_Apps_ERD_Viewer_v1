# Changelog

All notable changes to ERD Viewer will be documented in this file.

## [2.0.0] - 2025-10-23

### Changed
- **🎉 MAJOR UPGRADE: Replaced Mermaid.js with Cytoscape.js** for significantly better ERD visualization
  - **Better Performance**: Handles 100+ tables smoothly (vs 30-40 with Mermaid)
  - **Superior Layouts**: Force-directed, hierarchical, circle, and grid layout algorithms
  - **True Interactivity**: Drag-and-drop tables to reposition them
  - **Native Zoom & Pan**: Smooth mouse wheel zoom, better touch support
  - **Dynamic Node Sizing**: Tables automatically sized based on content
  - **Better Relationship Rendering**: Smoother curved edges with arrows
  - **Professional Look**: Cleaner, more polished visualization

### Added
- **Multiple Layout Options**: Switch between 4 different layout algorithms on-the-fly
- **Drag & Drop**: Click and drag any table to reposition it
- **Fit to Screen**: Auto-fit entire diagram with one click
- **Double-Click Focus**: Double-click any table to zoom and center on it
- **Visual Indicators**: Color-coded borders for tables with relationships
  - Blue border: Has foreign keys (child table)
  - Green border: Is referenced (parent table)
  - Yellow border: Both child and parent
- **Enhanced Click Feedback**: Visual animation when clicking tables

### Removed
- Dependency on `streamlit-mermaid` (outdated package)
- Name sanitization requirements (Cytoscape handles special characters natively)
- Layout limitations (no longer constrained by Mermaid's ERD syntax)

### Technical Details
- Migrated from Mermaid ERD syntax to Cytoscape.js graph format
- Uses Cytoscape's cose-bilkent algorithm for optimal force-directed layouts
- Implements dagre for hierarchical top-down layouts
- All existing features preserved: search, filter, table details, etc.

## [1.0.1] - 2025-10-22

### Fixed
- **Mermaid Syntax Error with Multiple Tables**: Fixed syntax errors when generating ERDs for schemas with many tables
  - Improved sanitization of table names (handles special characters: `-`, `.`, `$`, etc.)
  - Improved sanitization of column names (handles special characters)
  - Simplified complex Databricks types for Mermaid display:
    - `struct<field:type>` → `struct`
    - `array<type>` → `array`
    - `map<key,value>` → `map`
    - `varchar(255)` → `varchar`
    - `decimal(10,2)` → `decimal`
  - Changed constraint indicators from brackets `[PK, FK]` to underscores `_PK_FK` for better Mermaid compatibility
  - Shortened "NOT NULL" to "NN" to save space

- **Recursion Error on Startup**: Fixed infinite loop caused by excessive `st.rerun()` calls
  - Removed explicit `st.rerun()` calls (Streamlit handles this automatically)
  - Added unique keys to all interactive widgets
  - Fixed environment variable handling in connection form

### Technical Details
The Mermaid ERD syntax is strict about identifiers. This update ensures:
- All table and column names use only alphanumeric characters and underscores
- Special characters are replaced with underscores
- Names starting with numbers are prefixed
- Complex Databricks types are simplified for display
- All indicators use underscore-separated format

### Note
The ERD diagram shows sanitized names for Mermaid compatibility, but the **Table Details** panel at the bottom shows the original table/column names and types from Databricks.

## [1.0.0] - 2025-10-22

### Added
- Initial release
- Databricks Unity Catalog integration
- Interactive ERD generation with Mermaid
- Schema explorer with catalog/schema selection
- Zoom controls (50% - 200%)
- Table selection (multi-select)
- Table search (case-insensitive)
- Column search (case-insensitive)
- Minimize/maximize tables
- Adaptive view for large schemas
- Table details panel
- Relationship visualization (FK → PK)
- Complete documentation

