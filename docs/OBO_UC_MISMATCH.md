# OBO Authentication vs Unity Catalog Principal Mismatch

## The Issue You're Experiencing

✅ **Authentication**: Shows your email `my.email@databricks.com`  
❌ **Unity Catalog Access**: Only sees 2 schemas (default, information_schema)  
🤔 **Suspicion**: UC might still be using Service Principal despite OBO authentication

## Understanding the Two Layers

### Layer 1: Databricks Authentication (Workspace API)
- Uses the token from `x-forwarded-access-token` header
- The `current_user.me()` API uses this token
- Shows who you're **authenticated as**

### Layer 2: Unity Catalog Authorization
- Determines permissions for catalog/schema/table access
- Uses a principal identity for permission checks
- Shows what **permissions** are evaluated against

**These can be different!**

## The Diagnostic Test

The enhanced debug now runs:
```sql
SELECT current_user() as current_user
```

This query asks **Unity Catalog** who it thinks is making the request.

### Possible Outcomes:

#### Scenario A: Mismatch (OBO Not Working for UC)
```
DEBUG PERMISSIONS: Current auth identity: my.email@databricks.com
DEBUG PERMISSIONS: Unity Catalog sees principal: c77f1610-9bc8-41b1-9518-e117f6450feb
```
**Meaning**: 
- Authentication layer uses user token ✅
- Unity Catalog still uses Service Principal ❌
- **OBO is incomplete** - doesn't apply to UC queries

#### Scenario B: Match (OBO Working, Just Limited Permissions)
```
DEBUG PERMISSIONS: Current auth identity: my.email@databricks.com
DEBUG PERMISSIONS: Unity Catalog sees principal: my.email@databricks.com
```
**Meaning**:
- Both layers use your user identity ✅
- You genuinely only have access to 2 schemas
- **OBO is fully working**, you need more UC permissions

#### Scenario C: Both Show SP (OBO Not Working)
```
DEBUG PERMISSIONS: Current auth identity: c77f1610-9bc8-41b1-9518-e117f6450feb
DEBUG PERMISSIONS: Unity Catalog sees principal: c77f1610-9bc8-41b1-9518-e117f6450feb
```
**Meaning**:
- OBO token extraction failed
- Still using Service Principal everywhere
- Need to revisit token extraction

## If Scenario A (Mismatch)

This means the OAuth scopes don't include UC access. You need to:

### Check OAuth Scopes Configuration

Your OAuth client should have these scopes:
- ✅ `catalog.catalogs:read`
- ✅ `catalog.schemas:read`
- ✅ `catalog.tables:read`
- ✅ `sql` 

These scopes allow **reading** UC metadata, but might not be enough for the token to **authorize** UC queries.

### Possible Missing Scope

You might need an additional scope like:
- `unity-catalog` (if available)
- `catalog:*` (broader catalog access)
- Or Unity Catalog might need a separate OAuth configuration

### Solution Steps:

1. **Check if there's a separate UC OAuth configuration**
   - Go to App Settings
   - Look for "Unity Catalog Authorization" (separate from general User Authorization)
   - This might need to be enabled separately

2. **Verify OAuth Token Audience**
   - Your OAuth token might be scoped for Workspace API
   - UC might require a different token audience
   - Check if there's a "Token Audience" setting

3. **Contact Databricks Support**
   - This is a known complexity with OBO and Unity Catalog
   - Ask: "How do I configure OAuth for Unity Catalog access in Databricks Apps?"
   - Reference: OAuth client ID `8a4e3f1c-e7e8-4788-967c-338830ec9166`

## If Scenario B (Match - Both Show Email)

This is **good news**! OBO is fully working. You just need UC permissions.

### Request These Permissions:

```sql
-- For each catalog you need access to:
GRANT USE CATALOG ON CATALOG <catalog_name> TO `my.email@databricks.com`;

-- For specific schemas:
GRANT USE SCHEMA ON SCHEMA <catalog>.<schema> TO `my.email@databricks.com`;

-- To view table structures:
GRANT SELECT ON SCHEMA <catalog>.<schema> TO `my.email@databricks.com`;
```

### Or Join a Group:

Ask admin to add you to a group with broader permissions:
```sql
ALTER GROUP data_engineers ADD MEMBER `my.email@databricks.com`;
```

## Known Issue: OBO with Unity Catalog in Public Preview

Since "Databricks Apps - On-Behalf-Of User Authorization" is in **Public Preview**, there might be limitations:

### Known Limitations:
1. **UC API vs SQL Warehouse**: 
   - The SDK `schemas.list()` API might use different auth than SQL queries
   - SQL queries might honor OBO, but SDK APIs might not (or vice versa)

2. **Scope Mapping**:
   - OAuth scopes like `catalog.schemas:read` might not map to UC permission evaluation
   - UC might still evaluate against a default principal

3. **Token Propagation**:
   - The OBO token works for authentication
   - But UC permission checks might use a different mechanism

### Workaround (If UC Doesn't Support OBO Yet):

If UC cannot use OBO token, you might need to:
1. **Grant your user the same permissions as the SP** for testing
2. **Wait for full GA** of OBO with UC support
3. **Use SQL Warehouse queries** instead of SDK APIs (if those work with OBO)

## Next Steps

**Run the app and check the output:**

Look for this critical line:
```
DEBUG PERMISSIONS: Unity Catalog sees principal: ???????
```

### If it shows your email:
- OBO is fully working ✅
- Request UC permissions from admin
- See `VERIFY_PERMISSIONS.md`

### If it shows UUID:
- OBO works for auth but not UC ❌
- This is a configuration/limitation issue
- Contact Databricks support about UC OBO configuration
- Or grant your user account the needed permissions

---

**Key Question**: Does `SELECT current_user()` return your email or a UUID?

This will determine if the issue is OBO configuration or Unity Catalog permissions.


