# Unity Catalog Permissions Guide for ERD Viewer

## OBO is Working! But Why Can't I See My Schemas?

✅ **Good News**: OBO is working correctly - the app is using your user credentials!

❌ **Issue**: You're not seeing all the schemas you expect because of Unity Catalog permissions.

## Understanding Unity Catalog Permissions

When OBO is enabled, the app sees exactly what **YOUR USER ACCOUNT** can see in Unity Catalog - nothing more, nothing less.

### Required Permissions for ERD Viewer

To view schemas and tables in this app, you need:

#### 1. **Catalog Level**
```sql
-- User needs at least USE CATALOG permission
GRANT USE CATALOG ON CATALOG <catalog_name> TO `user@example.com`;
```

#### 2. **Schema Level**
```sql
-- User needs at least USE SCHEMA permission
GRANT USE SCHEMA ON SCHEMA <catalog_name>.<schema_name> TO `user@example.com`;
```

#### 3. **Table Level**
```sql
-- User needs at least SELECT permission to see table structure
GRANT SELECT ON TABLE <catalog_name>.<schema_name>.<table_name> TO `user@example.com`;

-- Or grant at schema level for all tables
GRANT SELECT ON SCHEMA <catalog_name>.<schema_name> TO `user@example.com`;
```

## Common Scenarios

### Scenario 1: Can't See Any Catalogs
**Symptom**: No catalogs appear in the dropdown

**Debug Output**:
```
DEBUG PERMISSIONS: Found 0 catalog(s): []
```

**Solution**: Ask your Databricks admin to grant:
```sql
GRANT USE CATALOG ON CATALOG <catalog_name> TO `user@example.com`;
```

### Scenario 2: Can See Catalog but No Schemas
**Symptom**: Select a catalog, but schema dropdown is empty

**Debug Output**:
```
DEBUG PERMISSIONS: Found 0 schema(s) in 'my_catalog': []
DEBUG PERMISSIONS: ⚠️ No schemas found.
```

**Solution**: You have `USE CATALOG` but not schema-level permissions. Ask admin:
```sql
GRANT USE SCHEMA ON SCHEMA <catalog_name>.<schema_name> TO `user@example.com`;
```

### Scenario 3: Can See Some Schemas but Not All
**Symptom**: You know schema X exists, but it's not in the list

**Explanation**: You only see schemas where you have at least `USE SCHEMA` permission. This is correct OBO behavior!

**Solution**: Request permission on specific schemas:
```sql
GRANT USE SCHEMA ON SCHEMA <catalog_name>.<missing_schema> TO `user@example.com`;
```

### Scenario 4: Can See Schema but No Tables
**Symptom**: Schema loads but "No tables" message appears

**Debug Output**:
```
DEBUG PERMISSIONS: Found 0 table(s) in 'my_catalog.my_schema'
```

**Solution**: You need SELECT permission on tables:
```sql
GRANT SELECT ON SCHEMA <catalog_name>.<schema_name> TO `user@example.com`;
```

## Checking Your Permissions

### Using SQL
Run these queries in a Databricks notebook to see what you have access to:

```sql
-- See all catalogs you can access
SHOW CATALOGS;

-- See schemas in a catalog
SHOW SCHEMAS IN <catalog_name>;

-- See tables in a schema
SHOW TABLES IN <catalog_name>.<schema_name>;

-- Check your grants
SHOW GRANTS ON CATALOG <catalog_name>;
SHOW GRANTS ON SCHEMA <catalog_name>.<schema_name>;
```

### Using the Debug Output
The app now shows detailed debug output. Look for:

```
DEBUG PERMISSIONS: Current user: your.email@company.com
DEBUG PERMISSIONS: Found X catalog(s): [list]
DEBUG PERMISSIONS: Found X schema(s) in 'catalog': [list]
```

Compare this with what you expect to see.

## OBO vs Service Principal Comparison

### Before OBO (Service Principal):
- App shows: What the **Service Principal** has access to
- All users see: The **same** catalogs/schemas
- Permissions needed: Grant to Service Principal

### After OBO (Your Implementation Now):
- App shows: What **YOUR USER** has access to
- Each user sees: Their **own** accessible catalogs/schemas
- Permissions needed: Grant to individual users or groups

## Granting Permissions (For Admins)

### Option 1: Grant to Individual User
```sql
-- Full access to specific schema
GRANT USE CATALOG ON CATALOG my_catalog TO `user@example.com`;
GRANT USE SCHEMA ON SCHEMA my_catalog.my_schema TO `user@example.com`;
GRANT SELECT ON SCHEMA my_catalog.my_schema TO `user@example.com`;
```

### Option 2: Grant to Group (Recommended)
```sql
-- Create or use existing group
CREATE GROUP data_analysts;
ALTER GROUP data_analysts ADD MEMBER `user@example.com`;

-- Grant to group
GRANT USE CATALOG ON CATALOG my_catalog TO data_analysts;
GRANT USE SCHEMA ON SCHEMA my_catalog.my_schema TO data_analysts;
GRANT SELECT ON SCHEMA my_catalog.my_schema TO data_analysts;
```

### Option 3: Grant at Higher Level
```sql
-- Grant on all schemas in a catalog
GRANT USE CATALOG ON CATALOG my_catalog TO `user@example.com`;
GRANT USE SCHEMA ON CATALOG my_catalog TO `user@example.com`;
GRANT SELECT ON CATALOG my_catalog TO `user@example.com`;
```

## Troubleshooting Checklist

When schemas don't appear:

1. ✅ **Verify OBO is working**
   - Look for: `DEBUG OBO: ✅ Using OBO token from headers`
   - If not, see `OBO_SETUP.md`

2. ✅ **Check current user**
   - Look for: `DEBUG PERMISSIONS: Current user: your.email@company.com`
   - Verify this is YOUR email, not a Service Principal

3. ✅ **Check catalog access**
   - Look for: `DEBUG PERMISSIONS: Found X catalog(s): [...]`
   - If 0 catalogs: You need `USE CATALOG` permission

4. ✅ **Check schema access**
   - Look for: `DEBUG PERMISSIONS: Found X schema(s) in 'catalog': [...]`
   - If 0 schemas: You need `USE SCHEMA` permission

5. ✅ **Verify expectations**
   - Run `SHOW SCHEMAS IN <catalog>` in SQL to confirm what you should see
   - Compare with app's debug output

## Still Having Issues?

### Check with Admin:
1. Who is the Unity Catalog admin?
2. What permissions do I have on catalog X?
3. Can you grant me access to schema Y?

### Verify in SQL:
```sql
-- This should show the same results as the app
SHOW CATALOGS;
SHOW SCHEMAS IN my_catalog;
SHOW TABLES IN my_catalog.my_schema;
```

### Compare Modes:
- Test with a user who has broad permissions
- If they see more schemas, it confirms permissions are the issue
- If they see the same, there might be a different problem

## Summary

🎉 **OBO is working!** You're seeing exactly what Unity Catalog thinks you should see.

If you need to see more schemas:
1. Identify which schemas you need access to
2. Contact your Databricks/Unity Catalog administrator
3. Request appropriate `USE CATALOG`, `USE SCHEMA`, and `SELECT` grants
4. Refresh the app once permissions are granted

The app is working correctly - it's showing your real Unity Catalog permissions! 🔒


