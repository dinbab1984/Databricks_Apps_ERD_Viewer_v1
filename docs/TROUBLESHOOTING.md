# 🔧 Troubleshooting Guide

Common issues and their solutions.

## ERD Rendering Issues

### Issue: Diagram Not Displaying

**Symptoms:**
- Blank white area where ERD should appear
- No tables visible
- Console may show JavaScript errors

**Cause:**
Usually related to browser compatibility or network issues loading Cytoscape.js libraries.

**Solution:**
✅ **Fixed in v1.0.1**

The application now:
- Sanitizes all table and column names (replaces special characters with underscores)
- Simplifies complex Databricks types:
  - `struct<field:type>` → `struct`
  - `array<type>` → `array`
  - `map<key,value>` → `map`
  - `varchar(255)` → `varchar`
  - `decimal(10,2)` → `decimal`

**What to do:**
1. Ensure you're using the latest version of the code
2. Restart the Streamlit app
3. Reload your schema

**Original names preserved:**
The Table Details panel at the bottom shows the original, unsanitized names and types.

---

## Recursion Error on Startup

### Issue: "RecursionError: maximum recursion depth exceeded"

**Symptoms:**
- App crashes on startup or after clicking Connect
- Browser shows endless loading
- Terminal shows recursion error stack trace

**Cause:**
Infinite loop caused by excessive `st.rerun()` calls in earlier versions.

**Solution:**
✅ **Fixed in v1.0.1**

The application now relies on Streamlit's automatic rerun mechanism instead of explicit `st.rerun()` calls.

**What to do:**
1. Kill any running Streamlit processes: `lsof -ti:8501 | xargs kill -9`
2. Ensure you're using the latest version
3. Restart the app: `streamlit run app.py`

---

## Connection Issues

### Issue: Cannot connect to Databricks

**Symptoms:**
- "Failed to connect to Databricks" error
- Authentication errors
- Timeout errors

**Possible Causes & Solutions:**

#### 1. Invalid Credentials
- **Check**: Verify your Databricks host URL format: `https://your-workspace.cloud.databricks.com`
- **Check**: Ensure your access token is valid and not expired
- **Solution**: Generate a new token from Databricks User Settings → Access Tokens

#### 2. Network Issues
- **Check**: Can you access your Databricks workspace URL in a browser?
- **Check**: Are you behind a corporate firewall/VPN?
- **Solution**: Ensure network access to Databricks, connect to VPN if required

#### 3. Insufficient Permissions
- **Check**: Does your token have read access to Unity Catalog?
- **Solution**: Create a new token with appropriate permissions or contact your Databricks admin

---

## No Tables Showing

### Issue: Schema loads but no tables appear

**Symptoms:**
- Schema loads successfully
- "No tables found matching criteria" message
- Empty ERD diagram

**Possible Causes & Solutions:**

#### 1. Empty Schema
- **Check**: Does the schema actually contain tables?
- **Solution**: Verify in Databricks that the schema has tables

#### 2. Active Filters
- **Check**: Are search filters or table selection active?
- **Solution**: Click "Reset View" or clear all filters

#### 3. Permissions
- **Check**: Do you have SELECT permission on the tables?
- **Solution**: Contact your Databricks admin for table access

---

## Diagram Not Rendering

### Issue: ERD diagram area is blank or shows loading indefinitely

**Symptoms:**
- Tables load but diagram doesn't appear
- White/blank area where diagram should be
- No error messages

**Possible Causes & Solutions:**

#### 1. Browser Issues
- **Check**: Open browser console (F12) for JavaScript errors
- **Solution**: Try a different browser (Chrome, Firefox, Safari)
- **Solution**: Clear browser cache

#### 2. Cytoscape.js CDN Not Accessible
- **Check**: Can you access https://cdnjs.cloudflare.com?
- **Solution**: Check internet connection or firewall settings
- **Solution**: Check if CDN is blocked by firewall

#### 3. Too Many Tables
- **Check**: Are you trying to display 100+ tables at once?
- **Solution**: Use table selection to display fewer tables
- **Solution**: Use search to filter tables

---

## Performance Issues

### Issue: App is slow or unresponsive

**Symptoms:**
- Long load times
- UI freezes
- Slow interactions

**Possible Causes & Solutions:**

#### 1. Large Schema
- **Problem**: Schema has 100+ tables or 1000+ columns
- **Solution**: Use table selection to view subsets
- **Solution**: Let the app auto-minimize tables
- **Solution**: Use search filters to reduce visible tables

#### 2. Complex Types
- **Note**: Complex Databricks types (struct, array, map) are now simplified
- **Solution**: Already handled in v1.0.1

#### 3. Slow Databricks API
- **Check**: Is your Databricks workspace responding slowly?
- **Solution**: Try again later or contact Databricks support

---

## Installation Issues

### Issue: Dependencies won't install

**Symptoms:**
- `pip install` fails
- Module not found errors
- Version conflicts

**Solutions:**

#### 1. Python Version
- **Check**: Ensure Python 3.8 or higher: `python3 --version`
- **Solution**: Upgrade Python if needed

#### 2. Virtual Environment
- **Solution**: Always use a virtual environment:
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  pip install -r requirements.txt
  ```

#### 3. Pip Upgrade
- **Solution**: Upgrade pip first:
  ```bash
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

#### 4. Network Issues
- **Check**: Can pip access PyPI?
- **Solution**: Try with a different network or use a proxy

---

## Zoom Not Working

### Issue: Zoom slider doesn't affect diagram

**Symptoms:**
- Moving zoom slider has no effect
- Diagram size doesn't change

**Solutions:**

1. **Refresh the page**: Sometimes the initial render needs a refresh
2. **Click Reset View**: Reset all view settings
3. **Check browser zoom**: Browser zoom conflicts with app zoom - reset browser zoom to 100%

---

## Table Details Not Showing

### Issue: Bottom panel is empty or shows wrong table

**Symptoms:**
- No table details displayed
- Details don't update when selecting different table

**Solutions:**

1. **Ensure schema is loaded**: Details only appear after loading a schema
2. **Select a table**: Use the dropdown to select a table
3. **Refresh**: Click "Load Schema" again to reload metadata

---

## Environment Variables Not Working

### Issue: App doesn't use DATABRICKS_HOST or DATABRICKS_TOKEN

**Symptoms:**
- Need to enter credentials every time
- Environment variables seem ignored

**Solutions:**

1. **Export variables correctly**:
   ```bash
   export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
   export DATABRICKS_TOKEN="your-token"
   ```

2. **Run from same terminal**: Environment variables only exist in the terminal session where they were set

3. **Use .env file**: Create a `.env` file (not tracked by git):
   ```
   DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
   DATABRICKS_TOKEN=your-token
   ```

4. **Check Streamlit doesn't reload environment**: Streamlit may not pick up env changes while running

---

## Getting Help

If your issue isn't listed here:

1. **Check the logs**: Look at terminal output for error messages
2. **Check browser console**: Open Developer Tools (F12) and check Console tab
3. **Review documentation**:
   - `README.md` - User guide
   - `ARCHITECTURE.md` - Technical details
   - `QUICK_START.md` - Setup guide

4. **Common debugging steps**:
   ```bash
   # Kill all Streamlit processes
   lsof -ti:8501 | xargs kill -9
   
   # Clear Python cache
   rm -rf __pycache__
   
   # Restart with fresh environment
   deactivate  # if in venv
   source venv/bin/activate
   streamlit run app.py
   ```

5. **Test with minimal schema**: Try loading a small schema (5-10 tables) to isolate the issue

---

## Known Limitations

Current limitations of the application:

1. **Read-Only**: No write operations to Unity Catalog (by design)
2. **Single Schema**: Can only view one schema at a time
3. **Very Large Schemas**: 200+ tables may require performance tuning or filtering
4. **No Export**: Currently no SVG/PNG export (planned for future release)
5. **No History**: Schema changes over time are not tracked

---

**Version**: 1.0.1  
**Last Updated**: October 2025

For persistent issues, please check the project repository or contact support.

