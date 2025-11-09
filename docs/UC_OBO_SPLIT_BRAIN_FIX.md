# Unity Catalog OBO Split-Brain Issue - CONFIRMED

## 🔴 Issue Confirmed

```
Authentication API: my.email@databricks.com  ✅ (User)
Unity Catalog:      29ac56fe-a78c-49fa-b731-97906f8e246d  ❌ (Service Principal UUID)
```

**This is a "split-brain" issue** - different Databricks APIs use different principals!

## Root Cause

The OAuth token works for:
- ✅ Workspace API (`current_user.me()`)
- ✅ General authentication
- ❌ **Unity Catalog permission evaluation**

Unity Catalog is still using the Service Principal for permission checks despite the OBO token being present.

## Why This Happens

### Possible Reasons:

1. **OAuth Scopes Don't Cover UC Permission Evaluation**
   - Your scopes (`catalog.catalogs:read`, etc.) allow reading metadata
   - But don't grant the token authority for **permission evaluation**
   - UC might need a different scope like `unity-catalog:access` or similar

2. **UC Requires Separate OAuth Configuration**
   - Workspace-level OBO might be enabled
   - But UC-specific OBO might need separate configuration

3. **Public Preview Limitation**
   - UC support for OBO might be incomplete in Public Preview
   - Some APIs honor it, others don't

4. **SDK API vs SQL Warehouse**
   - SDK's `catalogs.list()`, `schemas.list()` APIs might use different auth
   - SQL warehouse queries might honor OBO better

## Solution Attempts

### Option 1: Use SQL Warehouse Instead of SDK APIs

The SDK APIs might not support OBO for UC yet, but SQL queries might.

Replace SDK catalog operations with SQL:

```python
# Instead of: self.client.schemas.list(catalog_name)
# Use SQL:
query = f"SHOW SCHEMAS IN {catalog_name}"
result = self._execute_sql_query(query)
```

**Advantage**: SQL warehouse definitely gets your user token
**Disadvantage**: Different data format, slower

### Option 2: Check for Additional UC OAuth Settings

In Databricks UI, look for:

**Apps → Your App → Settings:**
- Look beyond "User Authorization"
- Check for "Unity Catalog" specific section
- Look for "Advanced" or "Beta Features"

**Workspace Settings → Admin Console:**
- Unity Catalog settings
- OAuth/OBO settings specific to UC
- "Allow apps to access UC on behalf of users"

### Option 3: Request UC-Specific OAuth Scope

Contact Databricks support and ask:
```
"I have OBO working for Workspace API (authentication shows user email), 
but Unity Catalog queries still use Service Principal UUID for permission 
checks. What OAuth scope or configuration is needed for UC permission 
evaluation to use the user's token?"

OAuth Client ID: 8a4e3f1c-e7e8-4788-967c-338830ec9166
Current scopes: catalog.catalogs:read, catalog.schemas:read, catalog.tables:read, sql
Issue: SELECT current_user() returns SP UUID instead of user email
```

### Option 4: Grant Your User the Same Permissions as SP

**Temporary workaround** until UC OBO is fully working:

Ask admin to grant you the same UC permissions the Service Principal has:

```sql
-- Get SP permissions
SHOW GRANTS ON CATALOG <catalog> FOR SERVICE_PRINCIPAL `29ac56fe-a78c-49fa-b731-97906f8e246d`;

-- Grant same to you
GRANT USE CATALOG ON CATALOG <catalog> TO `my.email@databricks.com`;
GRANT USE SCHEMA ON SCHEMA <catalog>.<schema> TO `my.email@databricks.com`;
GRANT SELECT ON SCHEMA <catalog>.<schema> TO `my.email@databricks.com`;
```

This way, even though UC uses SP for auth checks, your user has equivalent access.

## Verification Checklist

- [x] OBO enabled at workspace level ✅
- [x] OAuth consent completed ✅
- [x] User email shows in authentication ✅
- [ ] UC sees user email (not UUID) ❌ **FAILING HERE**
- [ ] Can see all schemas you have access to ❌

## The Blocker

The issue is **NOT in your code** - it's in how Databricks Apps' OBO feature integrates with Unity Catalog in Public Preview.

Your implementation is correct. Unity Catalog just doesn't honor the OBO token for permission evaluation yet (or needs additional configuration we haven't found).

## Recommended Next Steps

1. **Contact Databricks Support** with this specific question:
   - "How do I configure OBO so Unity Catalog permission checks use the user token?"
   - Share that `SELECT current_user()` returns SP UUID despite OBO being enabled
   - Request the specific configuration or scope needed

2. **Check Databricks Documentation** for:
   - "Unity Catalog with OBO"
   - "Apps OAuth with Unity Catalog"
   - Public Preview limitations

3. **Consider Temporary Workaround**:
   - Grant your user account the necessary UC permissions
   - Continue using OBO for audit trail (shows user email)
   - Accept that permission checks still use SP level until GA

4. **Try SQL Warehouse Approach**:
   - Modify code to use SQL queries instead of SDK APIs
   - Test if `SHOW SCHEMAS` returns different results

## Expected Timeline

Since this is a **Public Preview feature**, full Unity Catalog integration might:
- Be fully supported in GA release
- Require additional configuration we haven't discovered
- Need a Databricks platform update

Your code is correct. The limitation is at the Databricks platform level for UC + OBO integration.

---

**Status**: OBO working for auth, NOT working for UC permission evaluation  
**Blocker**: Platform limitation or missing configuration
**Recommendation**: Contact Databricks support for UC+OBO configuration


