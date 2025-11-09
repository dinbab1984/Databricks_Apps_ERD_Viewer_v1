"""
Reusable UI Components
"""
import streamlit.components.v1 as components
import streamlit as st
import json
import base64


def render_cytoscape(elements: dict, zoom: int = 100, schema_metadata: dict = None):
    """
    Render Cytoscape.js diagram with elegant HTML table overlays and integrated panels
    
    Args:
        elements: Dictionary with 'nodes' and 'edges' lists
        zoom: Zoom level percentage (default 100)
        schema_metadata: Full schema metadata for table details panel
    """
    # Safe data transmission via base64
    elements_json_str = json.dumps(elements)
    elements_b64 = base64.b64encode(elements_json_str.encode('utf-8')).decode('ascii')
    
    # Prepare table metadata for the details panel
    if schema_metadata is None:
        schema_metadata = {}
    metadata_json_str = json.dumps(schema_metadata)
    metadata_b64 = base64.b64encode(metadata_json_str.encode('utf-8')).decode('ascii')
    
    # Get list of visible tables
    visible_tables = list(schema_metadata.keys())
    
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
        <script src="https://unpkg.com/dagre@0.8.5/dist/dagre.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/cytoscape-dagre@2.5.0/cytoscape-dagre.min.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8f9fa; overflow: hidden; }
            #cy { width: 100%; height: 100vh; background: white; }
            
            /* ERD Table Styles */
            .erd-table {
                background: white; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                overflow: hidden; min-width: 250px; font-family: 'Monaco', 'Consolas', monospace;
            }
            .erd-table-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 10px; font-weight: 600; font-size: 13px; text-align: center;
            }
            .erd-table-header.child { background: linear-gradient(135deg, #17a2b8 0%, #138496 100%); }
            .erd-table-header.parent { background: linear-gradient(135deg, #28a745 0%, #218838 100%); }
            .erd-table-header.both { background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%); }
            .erd-table table { width: 100%; border-collapse: collapse; background: white; }
            .erd-col-row { border-bottom: 1px solid #e9ecef; }
            .erd-col-row:last-child { border-bottom: none; }
            .erd-col-row:hover { background: #f0f8ff; }
            .erd-col-cell { padding: 6px 10px; font-size: 11px; }
            .erd-icon { display: inline-block; min-width: 45px; margin-right: 5px; }
            .erd-name { font-weight: 600; color: #2c3e50; }
            .erd-type { color: #7f8c8d; font-size: 10px; margin-left: 8px; }
            
            /* Panel Base Styles */
            .panel {
                position: fixed; background: rgba(255,255,255,0.98); border-radius: 10px;
                z-index: 1000; box-shadow: 0 8px 24px rgba(0,0,0,0.15); transition: all 0.3s;
            }
            .panel.minimized { padding: 10px !important; }
            .panel h4 {
                margin: 0 0 12px 0; font-size: 15px; color: #667eea; text-align: center;
                border-bottom: 2px solid #f0f0f0; padding-bottom: 8px; font-weight: 600;
                display: flex; align-items: center; justify-content: space-between;
            }
            .panel h4 .title { flex: 1; }
            .minimize-btn {
                background: none; border: none; color: #667eea; cursor: pointer; font-size: 16px;
                padding: 0; width: 24px; height: 24px; display: flex; align-items: center;
                justify-content: center; border-radius: 4px;
            }
            .minimize-btn:hover { background: #f0f0f0; }
            .panel-content { transition: all 0.3s; overflow: hidden; }
            .panel.minimized .panel-content { max-height: 0; opacity: 0; margin: 0; padding: 0; }
            
            /* Search Panel */
            #search-panel { top: 15px; left: 15px; padding: 15px; min-width: 300px; }
            .search-input {
                width: 100%; padding: 8px 12px; border: 2px solid #e9ecef; border-radius: 6px;
                font-size: 12px; margin-bottom: 8px;
            }
            .search-input:focus { border-color: #667eea; outline: none; }
            .search-hint { font-size: 10px; color: #6c757d; margin-top: 4px; }
            
            /* Table Details Panel - Floating Window */
            #details-panel { 
                position: fixed;
                top: 50%; 
                left: 50%; 
                transform: translate(-50%, -50%);
                padding: 15px; 
                min-width: 350px; 
                max-width: 450px; 
                max-height: 80vh;
                background: rgba(255,255,255,0.98);
                border-radius: 10px;
                z-index: 2000;
                box-shadow: 0 12px 40px rgba(0,0,0,0.25);
                display: none; /* Hidden by default */
                transition: all 0.3s;
            }
            #details-panel.visible { 
                display: block !important; 
                animation: fadeInScale 0.3s ease-out;
            }
            @keyframes fadeInScale {
                from { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
                to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
            }
            #details-panel .panel-content { overflow-y: auto; max-height: calc(80vh - 80px); }
            .close-btn {
                background: none; border: none; color: #dc3545; cursor: pointer; font-size: 18px;
                padding: 0; width: 24px; height: 24px; display: flex; align-items: center;
                justify-content: center; border-radius: 4px; margin-left: 4px;
            }
            .close-btn:hover { background: #fee; }
            .table-selector {
                width: 100%; padding: 8px; border: 2px solid #e9ecef; border-radius: 6px;
                font-size: 12px; margin-bottom: 12px; background: white;
            }
            .table-info { 
                background: #f8f9fa; padding: 10px; border-radius: 6px; margin-bottom: 10px;
                font-size: 11px;
            }
            .table-info-row { margin: 4px 0; }
            .column-list { 
                background: white; border-radius: 6px; border: 1px solid #dee2e6;
                max-height: 400px; overflow-y: auto;
            }
            .column-item {
                padding: 10px 12px; border-bottom: 1px solid #e9ecef; font-size: 11px;
                transition: background 0.2s;
            }
            .column-item:last-child { border-bottom: none; }
            .column-item:hover { background: #f0f8ff; }
            .table-info-row { 
                margin: 6px 0; 
                line-height: 1.5; 
                word-wrap: break-word;
            }
            .column-name { font-weight: 600; color: #2c3e50; }
            .column-type { color: #7f8c8d; font-size: 10px; margin-left: 8px; }
            
            /* ERD Controls Panel (Right Side) */
            #controls { top: 15px; right: 15px; padding: 15px; min-width: 220px; }
            .control-group { margin: 12px 0; }
            .control-label { font-size: 11px; color: #6c757d; margin-bottom: 6px; font-weight: 600; display: block; }
            .button-row { display: flex; gap: 6px; justify-content: center; }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
                border: none; padding: 9px 14px; border-radius: 6px; cursor: pointer;
                font-size: 12px; font-weight: 600; transition: all 0.2s;
            }
            button:hover { transform: translateY(-2px); }
            select { width: 100%; padding: 8px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 12px; background: white; }
            #zoom-display { text-align: center; font-size: 14px; color: #2c3e50; margin: 6px 0; font-weight: 600; }
            .legend { font-size: 11px; color: #6c757d; margin-top: 12px; padding-top: 12px; border-top: 2px solid #f0f0f0; }
            .legend-title { font-weight: 600; color: #495057; margin-bottom: 6px; }
            .legend-item { margin: 4px 0; }
        </style>
    </head>
    <body>
        <div id="cy"></div>
        
        <!-- Search Panel -->
        <div id="search-panel" class="panel">
            <h4><span class="title">🔍 Search</span>
            <button class="minimize-btn" onclick="togglePanel('search-panel')">➖</button></h4>
            <div class="panel-content">
                <input type="text" id="table-search" class="search-input" placeholder="Search tables..." 
                       oninput="handleTableSearch(this.value)">
                <div class="search-hint" id="table-search-hint">💡 Shows matching tables + related (FK)</div>
                <input type="text" id="column-search" class="search-input" placeholder="Search columns..." 
                       oninput="handleColumnSearch(this.value)">
                <div class="search-hint" id="column-search-hint">Case-insensitive column search</div>
            </div>
        </div>
        
        <!-- Table Details Panel - Floating Window -->
        <div id="details-panel" class="panel">
            <h4>
                <span class="title" id="details-panel-title">📋 Table Details</span>
                <button class="close-btn" onclick="closeTableDetails()" title="Close">✕</button>
            </h4>
            <div class="panel-content">
                <div id="table-details-content"></div>
            </div>
        </div>
        
        <!-- ERD Controls Panel -->
        <div id="controls" class="panel">
            <h4><span class="title">🎛️ ERD Controls</span>
            <button class="minimize-btn" onclick="togglePanel('controls')">➖</button></h4>
            <div class="panel-content">
                <div class="control-group">
                    <div class="control-label">Layout</div>
                    <select onchange="changeLayout(this.value)">
                        <option value="dagre">Hierarchical ⭐</option>
                        <option value="breadthfirst">Breadth First</option>
                        <option value="cose">Force Directed</option>
                        <option value="circle">Circle</option>
                        <option value="grid">Grid</option>
                    </select>
                </div>
                <div class="control-group">
                    <div class="control-label">Zoom</div>
                    <div id="zoom-display">100%</div>
                    <div class="button-row">
                        <button onclick="zoomOut()">➖</button>
                        <button onclick="resetView()">Reset</button>
                        <button onclick="zoomIn()">➕</button>
                    </div>
                </div>
                <div class="control-group">
                    <div class="button-row"><button onclick="fitToScreen()" style="width:100%">📐 Fit Screen</button></div>
                </div>
                <div class="control-group">
                    <div class="button-row"><button onclick="toggleFullscreen()" style="width:100%">⛶ Fullscreen</button></div>
                </div>
                <div class="legend">
                    <div class="legend-title">Legend</div>
                    <div class="legend-item">🔑 Primary Key</div>
                    <div class="legend-item">🔗 Foreign Key</div>
                    <div class="legend-item">⚠️ NOT NULL</div>
                </div>
            </div>
        </div>
        
        <script>
            const DATA = JSON.parse(atob('""" + elements_b64 + """'));
            const METADATA = JSON.parse(atob('""" + metadata_b64 + """'));
            let cy, currentLayout = 'dagre', overlays = {};
            
            if (typeof cytoscape !== 'undefined' && typeof dagre !== 'undefined') {
                cytoscape.use(cytoscapeDagre);
            }
            
            function createTableHTML(node) {
                const name = node.data('label');
                const cols = node.data('columns') || [];
                const hasFk = node.data('has_fk');
                const isRef = node.data('is_referenced');
                
                let hClass = '';
                if (hasFk && isRef) hClass = 'both';
                else if (hasFk) hClass = 'child';
                else if (isRef) hClass = 'parent';
                
                let html = '<div class="erd-table"><div class="erd-table-header ' + hClass + '">' + name + '</div><table>';
                
                cols.slice(0, 12).forEach(function(col) {
                    let icons = '';
                    let text = col;
                    
                    if (col.includes('🔑')) { icons += '<span style="color:#ffc107">🔑</span>'; text = text.replace('🔑', ''); }
                    if (col.includes('🔗')) { icons += '<span style="color:#17a2b8">🔗</span>'; text = text.replace('🔗', ''); }
                    if (col.includes('⚠️')) { icons += '<span style="color:#fd7e14">⚠️</span>'; text = text.replace('⚠️', ''); }
                    if (!icons) icons = '<span style="opacity:0">　</span>';
                    
                    const parts = text.split(':');
                    const colName = parts[0].trim();
                    const colType = parts[1] ? parts[1].trim() : '';
                    
                    html += '<tr class="erd-col-row"><td class="erd-col-cell">';
                    html += '<span class="erd-icon">' + icons + '</span>';
                    html += '<span class="erd-name">' + colName + '</span>';
                    if (colType) html += '<span class="erd-type">' + colType + '</span>';
                    html += '</td></tr>';
                });
                
                if (cols.length > 12) {
                    html += '<tr class="erd-col-row"><td class="erd-col-cell" style="text-align:center;color:#999;font-style:italic">... (' + node.data('column_count') + ' total)</td></tr>';
                }
                
                html += '</table></div>';
                return html;
            }
            
            function updateOverlay(node, div) {
                const pos = node.renderedPosition();
                const z = cy.zoom();
                div.style.left = pos.x + 'px';
                div.style.top = pos.y + 'px';
                div.style.transform = 'translate(-50%, -50%) scale(' + z + ')';
            }
            
            function init() {
                cy = cytoscape({
                    container: document.getElementById('cy'),
                    elements: DATA,
                    style: [
                        { selector: 'node', style: { 'background-opacity': 0, 'border-width': 0, 'width': 250, 
                          'height': function(ele) { const c = ele.data('columns') || []; return 35 + Math.min(c.length, 12) * 24 + (c.length > 12 ? 24 : 0); },
                          'shape': 'rectangle', 'label': '' } },
                        { selector: 'edge', style: { 'width': 2.5, 'line-color': '#667eea', 'target-arrow-color': '#667eea',
                          'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'arrow-scale': 1.8,
                          'label': 'data(label)', 'font-size': '9px', 'text-rotation': 'autorotate',
                          'color': '#495057', 'text-background-color': 'white', 'text-background-opacity': 0.9 } }
                    ],
                    layout: { name: 'preset' },
                    minZoom: 0.15, maxZoom: 2.5
                });
                
                cy.nodes().forEach(function(node) {
                    const div = document.createElement('div');
                    div.innerHTML = createTableHTML(node);
                    div.style.position = 'absolute';
                    div.style.transformOrigin = 'center center';
                    div.style.zIndex = '1';
                    div.style.pointerEvents = 'none'; // Allow clicks to pass through to Cytoscape
                    div.setAttribute('data-table-name', node.data('label')); // Store table name for reference
                    document.body.appendChild(div);
                    overlays[node.id()] = div;
                    updateOverlay(node, div);
                    
                    // Add click handler directly to the overlay
                    div.style.pointerEvents = 'auto'; // Re-enable pointer events
                    div.style.cursor = 'pointer';
                    div.onclick = function() {
                        const tableName = node.data('label');
                        console.log('Overlay clicked:', tableName);
                        showTableDetails(tableName);
                    };
                });
                
                cy.on('pan zoom resize', function() { cy.nodes().forEach(function(n) { if (overlays[n.id()]) updateOverlay(n, overlays[n.id()]); }); });
                cy.on('position', 'node', function(evt) { if (overlays[evt.target.id()]) updateOverlay(evt.target, overlays[evt.target.id()]); });
                cy.on('zoom', function() { document.getElementById('zoom-display').textContent = Math.round(cy.zoom() * 100) + '%'; });
                cy.on('tap', 'node', function(evt) { 
                    const tableName = evt.target.data('label');
                    console.log('Node tapped:', tableName);
                    showTableDetails(tableName);
                    window.parent.postMessage({ type: 'table_click', table: tableName }, '*'); 
                });
                
                runLayout(currentLayout);
            }
            
            function showTableDetails(tableName) {
                console.log('showTableDetails called with:', tableName);
                const panel = document.getElementById('details-panel');
                const title = document.getElementById('details-panel-title');
                const content = document.getElementById('table-details-content');
                
                console.log('Panel element:', panel);
                console.log('Has metadata:', !!METADATA[tableName]);
                
                if (!tableName || !METADATA[tableName]) {
                    console.log('No table or metadata, hiding panel');
                    panel.classList.remove('visible');
                    return;
                }
                
                // Update title with table name
                title.textContent = '📋 ' + tableName;
                console.log('Updated title to:', title.textContent);
                
                const table = METADATA[tableName];
                let html = '<div class="table-info">';
                
                // Table type and column count
                html += '<div class="table-info-row"><strong>Type:</strong> ' + (table.table_type || 'TABLE') + ' | <strong>Columns:</strong> ' + table.columns.length + '</div>';
                
                // Table description/comment
                if (table.comment && table.comment.trim()) {
                    html += '<div class="table-info-row"><strong>📝 Description:</strong><br/>' + table.comment + '</div>';
                }
                
                // Tags
                if (table.tags && Object.keys(table.tags).length > 0) {
                    html += '<div class="table-info-row"><strong>🏷️ Tags:</strong><br/>';
                    Object.keys(table.tags).forEach(function(key) {
                        html += '<span style="background:#e9ecef;padding:2px 8px;border-radius:4px;margin:2px;display:inline-block;font-size:10px">';
                        html += key + ': ' + table.tags[key] + '</span> ';
                    });
                    html += '</div>';
                }
                
                // Primary Keys
                if (table.primary_keys && table.primary_keys.length > 0) {
                    html += '<div class="table-info-row"><strong>🔑 Primary Key:</strong> ' + table.primary_keys.join(', ') + '</div>';
                }
                
                // Foreign Keys - Detailed
                if (table.foreign_keys && table.foreign_keys.length > 0) {
                    html += '<div class="table-info-row"><strong>🔗 Foreign Keys (' + table.foreign_keys.length + '):</strong></div>';
                    table.foreign_keys.forEach(function(fk) {
                        html += '<div style="margin-left:15px;font-size:10px;padding:4px 0">';
                        html += '• <strong>' + (fk.child_columns ? fk.child_columns.join(', ') : 'N/A') + '</strong>';
                        html += ' → <em>' + (fk.parent_table || 'N/A') + '</em>';
                        if (fk.parent_columns && fk.parent_columns.length > 0) {
                            html += ' (<strong>' + fk.parent_columns.join(', ') + '</strong>)';
                        }
                        if (fk.constraint_name) {
                            html += '<br/><span style="color:#999">   ' + fk.constraint_name + '</span>';
                        }
                        html += '</div>';
                    });
                }
                
                html += '</div>';
                
                html += '<div style="margin-top:12px;padding-top:12px;border-top:2px solid #f0f0f0">';
                html += '<div style="font-weight:600;color:#495057;margin-bottom:8px;font-size:12px">📊 Columns (' + table.columns.length + ')</div>';
                html += '</div>';
                
                html += '<div class="column-list">';
                table.columns.forEach(function(col) {
                    let symbols = '';
                    let constraints = [];
                    
                    if (table.primary_keys && table.primary_keys.includes(col.name)) {
                        symbols += '<span style="color:#ffc107;font-weight:bold">🔑</span> ';
                        constraints.push('<span style="background:#fff3cd;color:#856404;padding:1px 4px;border-radius:3px;font-size:9px">PK</span>');
                    }
                    
                    let isFk = false;
                    let fkTarget = '';
                    if (table.foreign_keys) {
                        table.foreign_keys.forEach(function(fk) {
                            if (fk.child_columns && fk.child_columns.includes(col.name)) {
                                isFk = true;
                                fkTarget = fk.parent_table;
                            }
                        });
                    }
                    if (isFk) {
                        symbols += '<span style="color:#17a2b8;font-weight:bold">🔗</span> ';
                        constraints.push('<span style="background:#d1ecf1;color:#0c5460;padding:1px 4px;border-radius:3px;font-size:9px">FK → ' + fkTarget.split('.').pop() + '</span>');
                    }
                    
                    if (!col.nullable) {
                        symbols += '<span style="color:#fd7e14;font-weight:bold">⚠️</span> ';
                        constraints.push('<span style="background:#f8d7da;color:#721c24;padding:1px 4px;border-radius:3px;font-size:9px">NOT NULL</span>');
                    } else {
                        constraints.push('<span style="background:#e9ecef;color:#6c757d;padding:1px 4px;border-radius:3px;font-size:9px">NULLABLE</span>');
                    }
                    
                    html += '<div class="column-item">';
                    html += '<div>';
                    html += symbols + '<span class="column-name">' + col.name + '</span>';
                    html += '<span class="column-type">' + col.type + '</span>';
                    html += '</div>';
                    
                    // Show constraints
                    if (constraints.length > 0) {
                        html += '<div style="margin-top:4px;margin-left:50px">' + constraints.join(' ') + '</div>';
                    }
                    
                    // Show column comment
                    if (col.comment && col.comment.trim()) {
                        html += '<div style="font-size:10px;color:#666;margin-top:4px;margin-left:50px;font-style:italic">';
                        html += '💬 ' + col.comment;
                        html += '</div>';
                    }
                    
                    // Show default value
                    if (col.default_value) {
                        html += '<div style="font-size:10px;color:#999;margin-top:2px;margin-left:50px">';
                        html += 'Default: <code style="background:#f8f9fa;padding:1px 4px;border-radius:2px">' + col.default_value + '</code>';
                        html += '</div>';
                    }
                    
                    html += '</div>';
                });
                html += '</div>';
                
                content.innerHTML = html;
                
                // Show the panel
                console.log('Adding visible class to panel');
                panel.classList.add('visible');
                console.log('Panel classes:', panel.className);
                console.log('Panel display style:', window.getComputedStyle(panel).display);
            }
            
            function closeTableDetails() {
                const panel = document.getElementById('details-panel');
                panel.classList.remove('visible');
            }
            
            function handleTableSearch(value) {
                const searchLower = value.toLowerCase().trim();
                
                if (!searchLower) {
                    // Show all nodes and edges
                    cy.nodes().style('display', 'element');
                    cy.edges().style('display', 'element');
                    Object.keys(overlays).forEach(function(id) {
                        overlays[id].style.display = 'block';
                    });
                    // Reset hint
                    const hint = document.getElementById('table-search-hint');
                    hint.textContent = '💡 Shows matching tables + related (FK)';
                    hint.style.color = '#6c757d';
                    
                    cy.fit(60);
                    return;
                }
                
                // Find matching tables and their related tables (via FK)
                const matchingNodes = new Set();
                const relatedNodes = new Set();
                
                cy.nodes().forEach(function(node) {
                    const tableName = node.data('label').toLowerCase();
                    if (tableName.includes(searchLower)) {
                        matchingNodes.add(node.id());
                    }
                });
                
                // Add related tables (parents and children via FK relationships)
                matchingNodes.forEach(function(nodeId) {
                    const node = cy.getElementById(nodeId);
                    
                    // Find connected edges and related nodes
                    node.connectedEdges().forEach(function(edge) {
                        const sourceId = edge.source().id();
                        const targetId = edge.target().id();
                        relatedNodes.add(sourceId);
                        relatedNodes.add(targetId);
                    });
                });
                
                const visibleNodes = new Set([...matchingNodes, ...relatedNodes]);
                
                // Hide/show nodes and overlays
                cy.nodes().forEach(function(node) {
                    if (visibleNodes.has(node.id())) {
                        node.style('display', 'element');
                        if (overlays[node.id()]) overlays[node.id()].style.display = 'block';
                    } else {
                        node.style('display', 'none');
                        if (overlays[node.id()]) overlays[node.id()].style.display = 'none';
                    }
                });
                
                // Hide/show edges
                cy.edges().forEach(function(edge) {
                    const source = edge.source().id();
                    const target = edge.target().id();
                    if (visibleNodes.has(source) && visibleNodes.has(target)) {
                        edge.style('display', 'element');
                    } else {
                        edge.style('display', 'none');
                    }
                });
                
                // Update hint with result count
                const hint = document.getElementById('table-search-hint');
                hint.textContent = '✓ Showing ' + visibleNodes.size + ' table(s) (including related)';
                hint.style.color = '#28a745';
                
                setTimeout(function() { cy.fit(60); }, 100);
            }
            
            function handleColumnSearch(value) {
                const searchLower = value.toLowerCase().trim();
                
                if (!searchLower) {
                    // Show all nodes and edges
                    cy.nodes().style('display', 'element');
                    cy.edges().style('display', 'element');
                    Object.keys(overlays).forEach(function(id) {
                        overlays[id].style.display = 'block';
                    });
                    
                    // Reset hint
                    const hint = document.getElementById('column-search-hint');
                    hint.textContent = 'Case-insensitive column search';
                    hint.style.color = '#6c757d';
                    
                    cy.fit(60);
                    return;
                }
                
                // Find tables that have columns matching the search
                const matchingNodes = new Set();
                
                Object.keys(METADATA).forEach(function(tableName) {
                    const table = METADATA[tableName];
                    if (table.columns) {
                        for (let i = 0; i < table.columns.length; i++) {
                            if (table.columns[i].name.toLowerCase().includes(searchLower)) {
                                // Find the node with this table name
                                cy.nodes().forEach(function(node) {
                                    if (node.data('label') === tableName) {
                                        matchingNodes.add(node.id());
                                    }
                                });
                                break;
                            }
                        }
                    }
                });
                
                // Hide/show nodes and overlays
                cy.nodes().forEach(function(node) {
                    if (matchingNodes.has(node.id())) {
                        node.style('display', 'element');
                        if (overlays[node.id()]) overlays[node.id()].style.display = 'block';
                    } else {
                        node.style('display', 'none');
                        if (overlays[node.id()]) overlays[node.id()].style.display = 'none';
                    }
                });
                
                // Show edges only between visible nodes
                cy.edges().forEach(function(edge) {
                    const source = edge.source().id();
                    const target = edge.target().id();
                    if (matchingNodes.has(source) && matchingNodes.has(target)) {
                        edge.style('display', 'element');
                    } else {
                        edge.style('display', 'none');
                    }
                });
                
                // Update hint with result count
                const hint = document.getElementById('column-search-hint');
                if (matchingNodes.size > 0) {
                    hint.textContent = '✓ Found in ' + matchingNodes.size + ' table(s)';
                    hint.style.color = '#28a745';
                } else {
                    hint.textContent = '⚠️ No tables found with this column';
                    hint.style.color = '#dc3545';
                }
                
                setTimeout(function() { cy.fit(60); }, 100);
            }
            
            function togglePanel(panelId) {
                const panel = document.getElementById(panelId);
                const btn = panel.querySelector('.minimize-btn');
                if (panel.classList.contains('minimized')) {
                    panel.classList.remove('minimized');
                    btn.textContent = '➖';
                } else {
                    panel.classList.add('minimized');
                    btn.textContent = '➕';
                }
            }
            
            function runLayout(name) {
                const opts = {
                    dagre: { name: 'dagre', rankDir: 'TB', nodeSep: 100, rankSep: 150, padding: 50, animate: true, animationDuration: 600 },
                    cose: { name: 'cose', animate: true, animationDuration: 600, nodeRepulsion: 400000, idealEdgeLength: 200, padding: 50 },
                    breadthfirst: { name: 'breadthfirst', directed: true, spacingFactor: 2, padding: 50, animate: true, animationDuration: 600 },
                    circle: { name: 'circle', animate: true, animationDuration: 600, padding: 80 },
                    grid: { name: 'grid', animate: true, animationDuration: 600, padding: 50, avoidOverlap: true }
                }[name];
                cy.layout(opts).run();
                setTimeout(function() { cy.fit(60); }, 700);
            }
            
            function changeLayout(name) { currentLayout = name; runLayout(name); }
            function zoomIn() { cy.zoom({ level: cy.zoom() * 1.25, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } }); }
            function zoomOut() { cy.zoom({ level: cy.zoom() * 0.8, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } }); }
            function resetView() { cy.zoom(1); cy.center(); }
            function fitToScreen() { cy.fit(70); }
            function toggleFullscreen() {
                const e = document.documentElement;
                if (!document.fullscreenElement) { if (e.requestFullscreen) e.requestFullscreen(); else if (e.webkitRequestFullscreen) e.webkitRequestFullscreen(); }
                else { if (document.exitFullscreen) document.exitFullscreen(); else if (document.webkitExitFullscreen) document.webkitExitFullscreen(); }
            }
            
            window.addEventListener('load', init);
            if (document.readyState === 'complete') init();
        </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=900, scrolling=False)
