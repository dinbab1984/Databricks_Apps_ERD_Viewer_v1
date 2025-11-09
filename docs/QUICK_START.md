# 🚀 Quick Start Guide

Get up and running with ERD Viewer in 5 minutes!

## Step 1: Install Dependencies

### Option A: Using the setup script (Recommended)
```bash
bash setup.sh
```

### Option B: Manual installation
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Databricks Connection

### Option A: Environment Variables (Recommended)
```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-access-token"
```

### Option B: In-App Configuration
You can also enter these values directly in the application's Connection Settings panel.

## Step 3: Run the Application

### Option A: Using the run script
```bash
bash run.sh
```

### Option B: Manual run
```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run Streamlit app
streamlit run app.py
```

## Step 4: Access the Application

Open your browser and navigate to:
```
http://localhost:8501
```

## Step 5: Generate Your First ERD

1. **Connect** (if you didn't set environment variables):
   - Click "Connection Settings" in the sidebar
   - Enter your Databricks Host and Token
   - Click "Connect"

2. **Select Schema**:
   - Choose a Catalog from the dropdown
   - Choose a Schema from the dropdown
   - Click "Load Schema"

3. **View and Customize**:
   - Your ERD will appear automatically
   - Use the controls to search, zoom, and filter
   - Scroll down to see detailed table information

## 🎯 Quick Tips

- **Large schemas?** The app auto-minimizes tables for better viewing
- **Looking for something?** Use the search boxes to filter tables or columns
- **Need details?** Check the "Table Details" section at the bottom
- **Can't see everything?** Use the zoom slider or minimize some tables

## 🆘 Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Verify your Databricks credentials have read access to Unity Catalog
- Ensure your network allows access to your Databricks workspace

## 📝 Getting a Databricks Token

1. Log in to your Databricks workspace
2. Click on your username in the top-right corner
3. Select "User Settings"
4. Go to "Access tokens" tab
5. Click "Generate new token"
6. Give it a name and set expiration
7. Copy the token (you won't be able to see it again!)

---

**Happy ERD Viewing! 🎉**

