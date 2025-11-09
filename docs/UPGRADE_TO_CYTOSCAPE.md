# 🎉 Upgrade to Cytoscape.js v2.0.0

## What Changed?

ERD Viewer has been upgraded from **Mermaid.js** to **Cytoscape.js** for significantly better ERD visualization and interactivity!

## 🚀 New Features

### Interactive Diagram
- **Drag & Drop Tables** - Click and drag any table to reposition it
- **Multiple Layouts** - Choose from 4 layout algorithms:
  - **Force-Directed** (default) - Organic, natural-looking layouts
  - **Hierarchical** - Top-down tree structure
  - **Circle** - Tables arranged in a circle
  - **Grid** - Organized grid layout

### Enhanced Interactivity
- **Better Zoom** - Smooth mouse wheel zoom
- **Better Pan** - Click and drag background to pan
- **Double-Click Focus** - Double-click any table to zoom and center on it
- **Visual Feedback** - Tables animate when clicked
- **Fit to Screen** - One-click to fit entire diagram in view

### Visual Improvements
- **Color-Coded Borders** - Tables with relationships are highlighted:
  - 🔵 Blue = Has foreign keys (child table)
  - 🟢 Green = Is referenced (parent table)  
  - 🟡 Yellow = Both child and parent
- **Better Relationship Lines** - Smoother curved arrows
- **Dynamic Sizing** - Tables automatically sized based on content

### Performance
- **100+ Tables** - Handles large schemas smoothly (vs 30-40 with Mermaid)
- **Faster Rendering** - Native graph visualization engine
- **Better Memory** - More efficient layout algorithms

## 📦 Migration Steps

### 1. Reinstall Dependencies

```bash
# Remove old virtual environment
rm -rf venv

# Run setup again (automatically installs correct dependencies)
bash setup.sh
```

### 2. Start the Application

```bash
bash run.sh
```

That's it! No code changes needed on your side.

## 🎮 How to Use New Features

### Change Layout
1. Look at the **Control Panel** in the top-right corner
2. Use the **Layout** dropdown to select:
   - Force Directed (best for most cases)
   - Hierarchical (good for clear parent-child relationships)
   - Circle (good for seeing all tables at once)
   - Grid (organized view)

### Reposition Tables
1. Click and hold on any table
2. Drag it to your desired position
3. The layout algorithm will adjust other tables automatically

### Zoom & Navigate
- **Zoom In/Out** - Use mouse wheel or `➕`/`➖` buttons
- **Pan** - Click and drag on empty space
- **Fit Screen** - Click "Fit Screen" button to see entire diagram
- **Reset** - Click "Reset" to return to default zoom
- **Focus Table** - Double-click any table to zoom to it

## 🔄 What Stayed the Same

All your existing workflows remain unchanged:
- ✅ Connect to Databricks
- ✅ Browse catalogs and schemas
- ✅ Search tables and columns
- ✅ View table details
- ✅ Filter relationships
- ✅ All keyboard shortcuts

## 📚 Updated Documentation

The following docs have been updated:
- ✅ `README.md` - Updated features and usage
- ✅ `docs/CHANGELOG.md` - Full v2.0.0 release notes
- ✅ `docs/ARCHITECTURE.md` - Updated technical details
- ✅ `docs/TROUBLESHOOTING.md` - Updated for Cytoscape

## 🐛 Troubleshooting

### Diagram Not Loading?
1. **Clear browser cache** - `Ctrl+Shift+Delete` or `Cmd+Shift+Delete`
2. **Check internet connection** - Cytoscape loads from CDN
3. **Try different browser** - Chrome, Firefox, or Safari

### Performance Issues?
1. **Use table filtering** - Select fewer tables to display
2. **Try hierarchical layout** - Often faster for large schemas
3. **Use search** - Filter to relevant tables only

### Tables Overlapping?
1. **Click "Fit Screen"** - Auto-arranges all tables
2. **Try different layout** - Switch between force-directed and hierarchical
3. **Drag tables manually** - Reposition as needed

## 🙋 Questions?

- Check the [README.md](README.md) for full documentation
- See [CHANGELOG.md](docs/CHANGELOG.md) for detailed release notes
- Review [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues

---

**Enjoy the enhanced ERD viewing experience! 🎊**




