# Databricks Deployment Guide

This guide explains how to deploy the ERD Viewer app to your Databricks workspace using Databricks Asset Bundles (DAB) and CLI.

## Prerequisites

### 1. Databricks CLI Installation

**Option A: Using pip**
```bash
pip install databricks-cli
```

**Option B: Using Homebrew (macOS)**
```bash
brew tap databricks/tap
brew install databricks
```

**Option C: Direct download**
- Download from: https://docs.databricks.com/dev-tools/cli/install.html

### 2. Verify Installation

```bash
databricks --version
```

### 3. Databricks Requirements

- Databricks workspace with Apps feature enabled
- Unity Catalog enabled
- Personal access token or OAuth authentication
- Appropriate permissions:
  - `CAN_MANAGE` on workspace
  - `USE_CATALOG` on Unity Catalog
  - `USE_SCHEMA` on schemas you want to visualize

## Authentication

### Method 1: Interactive Configuration

```bash
databricks configure --token
```

You'll be prompted for:
- **Databricks Host**: `https://your-workspace.databricks.com`
- **Token**: Your personal access token

### Method 2: Environment Variables

```bash
export DATABRICKS_HOST="https://your-workspace.databricks.com"
export DATABRICKS_TOKEN="dapi..."
```

### Method 3: Configuration File

Create `~/.databrickscfg`:

```ini
[DEFAULT]
host = https://your-workspace.databricks.com
token = dapi...
```

## Deployment Steps

### Step 1: Prepare the Project

Ensure you're in the project directory:

```bash
cd /path/to/erd_viewer
```

### Step 2: Validate Configuration

Test your bundle configuration:

```bash
databricks bundle validate
```

### Step 3: Deploy to Development

Deploy to your personal development environment:

```bash
bash deploy.sh dev
```

OR manually:

```bash
# Validate
databricks bundle validate -t dev

# Deploy
databricks bundle deploy -t dev

# Run
databricks bundle run erd_viewer_app -t dev
```

### Step 4: Deploy to Production (Optional)

Deploy to shared production environment:

```bash
bash deploy.sh prod
```

## Deployment Targets

### Development Target (`dev`)
- **Path**: `/Workspace/Users/your.email/.bundle/erd_viewer/dev`
- **Mode**: Development
- **Run As**: Your user account
- **Use for**: Testing, development, personal use

### Production Target (`prod`)
- **Path**: `/Workspace/Shared/.bundle/erd_viewer`
- **Mode**: Production
- **Run As**: Service principal (configurable)
- **Use for**: Team-wide deployment, production use

## Manual Deployment Commands

### Deploy without script

```bash
# Set target
TARGET=dev  # or prod

# Validate bundle
databricks bundle validate -t $TARGET

# Deploy to workspace
databricks bundle deploy -t $TARGET

# Start the app
databricks bundle run erd_viewer_app -t $TARGET

# Check deployment status
databricks bundle status -t $TARGET
```

### Update existing deployment

```bash
databricks bundle deploy -t dev --force
```

### Destroy deployment

```bash
databricks bundle destroy -t dev
```

## Accessing the Deployed App

### Via Databricks UI

1. Open your Databricks workspace
2. Navigate to **Apps** section (left sidebar)
3. Find your app: `erd-viewer-dev` or `erd-viewer-prod`
4. Click to open the app in a new tab

### Via Direct URL

The app URL will be in format:
```
https://your-workspace.databricks.com/apps/erd-viewer-dev
```

## Configuration

### Customize databricks.yml

Edit `databricks.yml` to customize:

**Resources**
```yaml
resources:
  - name: default
    description: "Main compute resource"
    cluster_id: "your-cluster-id"  # Optional: use specific cluster
```

**Environment Variables**
```yaml
env:
  - name: CUSTOM_VAR
    value: "custom_value"
```

**Compute Configuration**
```yaml
compute:
  - name: default
    cluster:
      spark_version: "13.3.x-scala2.12"
      node_type_id: "i3.xlarge"
      num_workers: 1
```

### Production Configuration

For production, edit the `prod` target in `databricks.yml`:

```yaml
targets:
  prod:
    mode: production
    workspace:
      root_path: /Workspace/Shared/.bundle/${bundle.name}
    run_as:
      service_principal_name: "erd-viewer-sp"  # Your service principal
```

## Troubleshooting

### Issue: "databricks: command not found"

**Solution**: Install Databricks CLI
```bash
pip install databricks-cli
```

### Issue: "Authentication required"

**Solution**: Configure authentication
```bash
databricks configure --token
```

Or set environment variables:
```bash
export DATABRICKS_HOST="https://..."
export DATABRICKS_TOKEN="dapi..."
```

### Issue: "Bundle validation failed"

**Solution**: Check `databricks.yml` syntax
```bash
databricks bundle validate -t dev
```

### Issue: "Permission denied"

**Solution**: Ensure you have necessary permissions:
- Workspace: `CAN_MANAGE`
- Unity Catalog: `USE_CATALOG`, `USE_SCHEMA`

### Issue: "App fails to start"

**Solution**: Check logs in Databricks Apps section
1. Go to Apps in workspace
2. Click on your app
3. View logs tab
4. Check for errors

### Issue: "Dependencies not installed"

**Solution**: Ensure `requirements.txt` is included in bundle:
```bash
# In databricks.yml, verify include section:
include:
  - "*.py"
  - "ui/**/*.py"
  - "requirements.txt"
```

## Monitoring & Maintenance

### View App Status

```bash
databricks bundle status -t dev
```

### View App Logs

Via Databricks UI:
1. Navigate to Apps
2. Select your app
3. Click "Logs" tab

### Update Deployment

After making code changes:

```bash
# Validate changes
databricks bundle validate -t dev

# Deploy update
databricks bundle deploy -t dev --force

# Restart app (if needed)
databricks bundle run erd_viewer_app -t dev
```

### Rollback

If you need to rollback:

```bash
# Option 1: Redeploy previous version
git checkout <previous-commit>
databricks bundle deploy -t dev --force

# Option 2: Destroy and redeploy
databricks bundle destroy -t dev
databricks bundle deploy -t dev
```

## Security Best Practices

1. **Use Service Principals for Production**
   - Create a dedicated service principal
   - Configure in `databricks.yml` under `prod.run_as`

2. **Limit Permissions**
   - Grant minimum required permissions
   - Use Unity Catalog data access policies

3. **Secure Tokens**
   - Use short-lived tokens
   - Rotate tokens regularly
   - Never commit tokens to version control

4. **Network Security**
   - Use workspace network policies
   - Enable IP access lists if needed

5. **Audit Logging**
   - Enable workspace audit logs
   - Monitor app access and usage

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy ERD Viewer

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Databricks CLI
        run: pip install databricks-cli
      
      - name: Deploy to Dev
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: |
          databricks bundle deploy -t dev
          
      - name: Deploy to Prod (on tag)
        if: startsWith(github.ref, 'refs/tags/')
        run: |
          databricks bundle deploy -t prod
```

## Additional Resources

- [Databricks Asset Bundles Documentation](https://docs.databricks.com/dev-tools/bundles/index.html)
- [Databricks CLI Reference](https://docs.databricks.com/dev-tools/cli/index.html)
- [Databricks Apps Documentation](https://docs.databricks.com/machine-learning/model-serving/create-manage-applications.html)
- [Unity Catalog Permissions](https://docs.databricks.com/data-governance/unity-catalog/manage-privileges/index.html)

## Support

For deployment issues:
1. Check [Troubleshooting](#troubleshooting) section above
2. Review Databricks workspace logs
3. Verify bundle configuration: `databricks bundle validate`
4. Check Databricks community forums

---

**Happy Deploying! 🚀**


