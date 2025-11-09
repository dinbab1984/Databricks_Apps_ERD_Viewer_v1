# Verify Unity Catalog Permissions - OBO is Working!

## 🎉 Great News: OBO IS WORKING!

You're seeing your real email: `my.email@databricks.com`

This means:
- ✅ The app is running as YOUR user
- ✅ The app sees what YOU have access to
- ✅ OBO is configured correctly

## 🔍 The Current Issue

You're not seeing all the schemas you **think** you have access to.

**This is expected behavior with OBO!** You now see exactly what Unity Catalog permissions you actually have - no more, no less.

## 📋 How to Verify Your Actual Permissions

### Step 1: Run This in a Databricks SQL Notebook

```sql
-- See all catalogs you have access to
SHOW CATALOGS;

-- For each catalog, check schemas
SHOW SCHEMAS IN <catalog_name>;

-- Check your actual grants
SHOW GRANTS ON CATALOG <catalog_name>;

-- See what schemas you can USE
USE CATALOG <catalog_name>;
SHOW SCHEMAS;
```

### Step 2: Compare with App Output

The app will now show detailed debug info:

```
============================================================
DEBUG PERMISSIONS: Listing schemas in catalog 'my_catalog'...
DEBUG PERMISSIONS: Using OBO: True
DEBUG PERMISSIONS: Querying as user: my.email@databricks.com
DEBUG PERMISSIONS: SDK returned X schema object(s)
  Schema 1: schema_name_1 (owner: ...)
  Schema 2: schema_name_2 (owner: ...)
DEBUG PERMISSIONS: Schema names: [list]
============================================================
```

**Compare the SDK output with your SQL query results.**

### Step 3: Understanding the Difference

#### Scenario A: SQL Shows More Schemas Than App

If `SHOW SCHEMAS IN catalog` returns **more schemas** than the app:

**Possible causes:**
1. **SELECT permission vs USE SCHEMA permission**
   - SQL `SHOW SCHEMAS` might show schemas you can see but can't use
   - SDK `list()` might only return schemas you have `USE SCHEMA` on

2. **Information_schema.schemata differences**
   - Different APIs may use different underlying queries
   - One might filter by `USE SCHEMA`, another by visibility

**Solution:** Check specific permissions:
```sql
-- For each missing schema, check:
SHOW GRANTS ON SCHEMA <catalog>.<missing_schema>;

-- You might need:
GRANT USE SCHEMA ON SCHEMA <catalog>.<schema> TO `my.email@databricks.com`;
```

#### Scenario B: App Shows What SQL Shows

If the numbers match, then you're seeing your **actual** permissions.

Before OBO, you saw the **Service Principal's** permissions (probably more).  
After OBO, you see **YOUR** permissions (might be less).

**This is correct behavior!**

## 🔑 Required Permissions for Schema to Appear

For a schema to appear in the app, you need:

### Minimum Required:
```sql
GRANT USE CATALOG ON CATALOG <catalog> TO `my.email@databricks.com`;
GRANT USE SCHEMA ON SCHEMA <catalog>.<schema> TO `my.email@databricks.com`;
```

### To See Table Details:
```sql
GRANT SELECT ON SCHEMA <catalog>.<schema> TO `my.email@databricks.com`;
-- OR for specific tables:
GRANT SELECT ON TABLE <catalog>.<schema>.<table> TO `my.email@databricks.com`;
```

## 🧪 Test: Compare Service Principal vs Your Access

To see the difference between SP and user permissions:

### 1. Check SP Permissions (what you saw before OBO):
```sql
-- Run as admin or check with admin
SHOW GRANTS ON CATALOG <catalog> FOR SERVICE_PRINCIPAL `<sp-uuid>`;
```

### 2. Check Your Permissions:
```sql
SHOW GRANTS ON CATALOG <catalog> FOR USER `my.email@databricks.com`;
```

The SP likely has **more** permissions than you do!

## 🎯 Next Steps

### Option 1: Request Missing Permissions

If you need access to specific schemas:

1. **Identify missing schemas** (compare SQL vs app output)
2. **Request permissions** from your Unity Catalog admin:
   ```
   Please grant me access to:
   - CATALOG: <catalog_name>
   - SCHEMA: <schema_name>
   
   Required permissions:
   - USE CATALOG
   - USE SCHEMA
   - SELECT (for viewing tables)
   ```

### Option 2: Use Group Membership

Ask admin to add you to groups that have the required permissions:

```sql
-- Admin runs:
ALTER GROUP data_engineers ADD MEMBER `my.email@databricks.com`;

-- Or:
ALTER GROUP data_analysts ADD MEMBER `my.email@databricks.com`;
```

### Option 3: Accept Current Permissions

If the missing schemas aren't needed, you're all set!

**OBO is working correctly - you're seeing your real permissions.**

## 📊 Debug Checklist

Run the app and check the debug output:

- [ ] `DEBUG PERMISSIONS: Querying as user: my.email@databricks.com` ← Your email
- [ ] `DEBUG PERMISSIONS: SDK returned X schema(s)` ← How many?
- [ ] Compare with `SHOW SCHEMAS IN catalog` results
- [ ] Check if numbers match or differ
- [ ] If differ, check individual schema grants

## 🎓 Understanding Unity Catalog Permission Model

Unity Catalog has hierarchical permissions:

```
CATALOG
  ├─ USE CATALOG ← Required to see it
  └─ SCHEMA
      ├─ USE SCHEMA ← Required to see it  
      └─ TABLE
          └─ SELECT ← Required to read data/structure
```

**Key Point:** Even if you can see a catalog, you might not have `USE SCHEMA` on all schemas within it.

The SDK's `list_schemas()` API might only return schemas where you have actual permissions, not just visibility.

## 🔄 Before OBO vs After OBO

### Before (Service Principal):
```
App queries → Uses SP credentials → SP has broad access → Shows many schemas
```
**You saw:** Everything the SP could access (not necessarily what YOU can access)

### After (OBO - Current):
```
App queries → Uses YOUR credentials → Limited to your grants → Shows your schemas
```
**You see:** Only what YOU actually have permission to access

## ✅ Success Criteria

OBO is successful when:
- ✅ Email shows your real email (not UUID) ← **YOU'RE HERE!**
- ✅ You see schemas you have USE SCHEMA permission on ← Verify this
- ✅ Different users see different schemas ← Test with colleague
- ✅ Audit logs show your email, not SP ← Check logs

---

**Current Status**: OBO is working! You're seeing your real permissions.  
**Action**: Verify your Unity Catalog grants match what the app shows.  
**Next**: Request additional permissions if needed, or you're done! 🎉


