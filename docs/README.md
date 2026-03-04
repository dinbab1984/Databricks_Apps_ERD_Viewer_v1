# ERD Viewer - Databricks Unity Catalog

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28.0-FF4B4B.svg)](https://streamlit.io)

A powerful, interactive Entity Relationship Diagram (ERD) viewer for Databricks Unity Catalog. Visualize your data warehouse schema with automatic relationship detection, search capabilities, and interactive exploration.

## ✨ Features

### Core Features
- 🔄 **Auto-generated ERDs** from Unity Catalog metadata
- 🔗 **Relationship Detection** - Based on UC defined FK/PK relationship mapping
- 🔍 **Smart Search** - Search tables and columns with related table inclusion
- 🎯 **Interactive** - Click tables/columns for detailed information
- 📊 **Table Selection** - Multi-select specific tables or view all
- 🗂️ **Tree Navigation** - Hierarchical catalog → schema → tables selection

### Advanced Features
- 🔎 **Advanced Zoom** - Buttons, mouse wheel, pinch zoom, double-click
- ⛶ **Fullscreen Mode** - Maximize ERD viewing area
- 🎨 **Modern UI** - Clean, compact design maximizing diagram space
- ⚡ **Performance Optimized** - Bulk constraint fetching for fast loading
- 📱 **Responsive** - Works on desktop and tablet devices
- 🎯 **Drag & Drop** - Reposition tables by dragging them
- 🔄 **Multiple Layouts** - Force-directed, hierarchical, circle, and grid layouts

### ERD Capabilities
- **Constraint Display** - PK (Primary Key), FK (Foreign Key), NOT NULL indicators
- **Relationship Lines** - Curved arrows showing table relationships with column labels
- **Data Types** - Shows column data types alongside names
- **Search Filtering** - Filter ERD by table name or column name
- **Related Tables** - Auto-includes parent/child tables when searching
- **Interactive Nodes** - Click to highlight, double-click to focus, drag to reposition

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Databricks workspace with Unity Catalog enabled
- Databricks personal access token

### Installation

1. **Clone or download the repository**
```bash
cd /path/to/erd_viewer
```

2. **Run the setup script**
```bash
bash setup.sh
```

This will:
- Create a Python virtual environment
- Install all required dependencies
- Prepare the application for use

3. **Configure connection (optional)**

Set environment variables:
```bash
export DATABRICKS_HOST="https://your-workspace.databricks.com"
export DATABRICKS_TOKEN="your-access-token"
```

Or use the UI to connect interactively.

### Running the Application

```bash
bash run.sh
```

The app will open at `http://localhost:8501`

## 📖 Usage

### Connecting to Databricks

1. **Enter connection details** in the sidebar:
   - **Host**: Your Databricks workspace URL
   - **Token**: Your personal access token

2. **Click Connect**

### Viewing ERDs

1. **Select a catalog** from the dropdown
2. **Select a schema** from the dropdown
3. **Click "Load"** to fetch metadata
4. **View the auto-generated ERD**

### Selecting Tables

**Mode 1: All Tables** (default)
- Shows all tables in the schema

**Mode 2: Select Specific**
- Multi-select specific tables from dropdown
- Check "Include related tables" to auto-add FK-connected tables

### Searching & Filtering

**Table Search**
- Enter table name to search
- Automatically includes related parent/child tables

**Column Search**
- Enter column name to filter
- Shows only tables with matching columns
- Highlights matching columns in ERD

### Interactive Features

**Control Panel** (top-right of ERD)
- **Layout Selector** - Choose between force-directed, hierarchical, circle, or grid
- **Zoom Controls** - `➕`/`➖` buttons and `Reset` button
- **Fit Screen** - Auto-fit entire diagram in view
- **Fullscreen** - Toggle fullscreen mode

**Mouse & Touch Interactions**
- **Drag tables** - Click and drag to reposition any table
- **Pan diagram** - Click and drag on empty space to pan
- **Zoom** - Mouse wheel to zoom in/out
- **Two-finger pinch** - Touch device zoom
- **Click table** - Highlights table and scrolls to details below
- **Double-click table** - Focus/zoom to that table

### Table Details Panel

- Located below the ERD diagram
- **Dropdown selector** - Choose any visible table
- **Synchronized filtering** - Shows only tables visible in ERD
- **Column information** - Name, type, nullable, constraints
- **Symbols**: 🔑 = PK, 🔗 = FK, ⚠️ = NOT NULL

## 📁 Project Structure

```
erd_viewer/
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── setup.sh                    # Setup script
├── run.sh                      # Run script
├── config.example.py           # Example configuration
├── app.py                      # Main application (orchestrator)
├── databricks_client.py        # Databricks API client
├── erd_generator.py            # ERD generation logic (Cytoscape.js)
├── ui/                         # UI modules (modular architecture)
│   ├── __init__.py
│   ├── components.py           # Cytoscape diagram component
│   ├── sidebar.py              # Sidebar & connection
│   ├── erd_controls.py         # Search & filters
│   ├── erd_diagram.py          # ERD rendering
│   └── table_details.py        # Table details panel
└── docs/                       # Documentation
    ├── QUICK_START.md          # Quick start guide
    ├── ARCHITECTURE.md         # Technical architecture
    ├── CHANGELOG.md            # Version history
    ├── TROUBLESHOOTING.md      # Common issues & solutions
    ├── PROJECT_SUMMARY.md      # Project overview
    └── REFACTORING_COMPLETE.md # Refactoring details
```

## 🔧 Configuration

### Environment Variables

```bash
# Databricks connection
export DATABRICKS_HOST="https://your-workspace.databricks.com"
export DATABRICKS_TOKEN="dapi..."
```

### Configuration File

Copy `config.example.py` to `config.py` and customize:

```python
# Databricks connection
DATABRICKS_HOST = "https://your-workspace.databricks.com"
DATABRICKS_TOKEN = "your-token-here"

# App settings
DEFAULT_ZOOM = 100
MAX_TABLES_TO_DISPLAY = 50
```

## 🛠️ Development

### Code Architecture

The application uses a **modular architecture** with clear separation of concerns:

- **app.py** - Main orchestrator, page config, session state
- **databricks_client.py** - Unity Catalog API interactions
- **erd_generator.py** - Cytoscape.js ERD data generation
- **ui/** - Reusable UI components organized by functionality

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

### Adding Features

1. Identify the appropriate module in `ui/`
2. Add your function to the module
3. Export it from `ui/__init__.py` if needed
4. Import and use in `app.py`

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests (when added)
pytest tests/
```

## 📚 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get started in 5 minutes
- **[Architecture](docs/ARCHITECTURE.md)** - Technical design & modules
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues & fixes
- **[Changelog](docs/CHANGELOG.md)** - Version history & updates
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Overview & features

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is provided as-is for internal use.

## 🙏 Acknowledgments

- **Streamlit** - Web application framework
- **Cytoscape.js** - Interactive graph visualization and ERD rendering
- **Databricks SDK** - Unity Catalog API access

## 📞 Support

For issues or questions:
1. Check [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
2. Review [Architecture Documentation](docs/ARCHITECTURE.md)
3. Open an issue with detailed information

---

**Built with ❤️ for data engineers working with Databricks Unity Catalog**
