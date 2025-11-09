# OBO (On-Behalf-Of) Setup Guide

## Current Status: ⚠️ OBO Not Enabled

Based on the debug logs, your Databricks App is running but **User Authorization is NOT enabled**, so it's using the Service Principal credentials instead of running as the logged-in user.

## Debug Log Analysis

```
DEBUG OBO: Available headers: ['Host', 'User-Agent', ..., 'X-Forwarded-Email', 
'X-Forwarded-User', 'X-Forwarded-Preferred-Username', ...]
DEBUG OBO: No OBO token found in any expected headers
DEBUG OBO: User token found: No
```

### What This Means:
- ✅ App is running in Databricks
- ✅ User identification headers are present (`X-Forwarded-Email`, `X-Forwarded-User`)
- ❌ **Missing**: `x-forwarded-access-token` header
- ❌ **Result**: App uses Service Principal (SP) permissions, not user permissions

## How to Enable OBO

### Step 1: Enable User Authorization in App Settings

1. Go to your Databricks workspace
2. Navigate to **Apps** > Your App > **Settings**
3. Find **Authentication** section
4. Enable **"User Authorization"** or **"Run as user"**
5. Save and redeploy the app

### Step 2: Verify OBO is Working

After enabling, you should see this in the logs:

```
DEBUG OBO: Found token in header 'x-forwarded-access-token' (length=XXX)
DEBUG OBO: ✅ Using OBO token from headers (token length: XXX)
```

### Step 3: Test User Permissions

Once OBO is enabled:
- Each user will see only the catalogs/schemas they have access to
- API calls run with the user's identity (not the Service Principal)
- Audit logs will show the actual user who made the request

## What The Code Does Now

### With OBO Disabled (Current):
```
User → Databricks App → Service Principal Token (DATABRICKS_TOKEN)
                     → API calls use SP permissions
                     → User sees what SP has access to
```

### With OBO Enabled (Target):
```
User → Databricks App → x-forwarded-access-token header
                     → API calls use USER permissions  
                     → User sees only their own data
```

## Verification Checklist

- [ ] User Authorization enabled in App settings
- [ ] App redeployed after settings change
- [ ] Log shows: "Found token in header 'x-forwarded-access-token'"
- [ ] Log shows: "✅ Using OBO token from headers"
- [ ] Users see different catalogs based on their permissions
- [ ] Audit logs show individual user names (not SP name)

## Troubleshooting

### Issue: OBO Token Found but Email is UUID (Service Principal)

**Symptom**: Logs show token is found, SDK reports "USER", but email is a UUID:
```
DEBUG OBO: Found token in header 'x-forwarded-access-token' (length=976)
DEBUG OBO: ✅ Using OBO token from headers
🔐 AUTHENTICATED AS:
   Type: SERVICE PRINCIPAL ⚠️
   SP UUID: c77f1610-9bc8-41b1-9518-e117f6450feb

❌ CRITICAL ISSUE: OBO TOKEN IS SERVICE PRINCIPAL TOKEN!
   The x-forwarded-access-token header contains the SP token,
   NOT the actual user's token.
```

**What This Means**: 
- The OBO header IS present
- A token IS being forwarded
- BUT it's the Service Principal's token, not the user's token
- This is the most common misconfiguration

**Root Cause**: The app authentication mode is set to **"Run as app"** instead of **"Run as user"**. When set to "Run as app", Databricks forwards the Service Principal's token in the header, not the user's token.

**Solution**:
1. Go to App Settings → Authentication
2. Look for "User Authorization" or "Run as" setting
3. Ensure it's set to **"Run as user"** (NOT "Run as app")
4. If you only see "Enable User Authorization", ensure it's ON
5. Save and **redeploy the app**
6. The token header should then contain the actual user's token

### Still Seeing Service Principal After Enabling OBO?

1. **Check App Settings**: Ensure "User Authorization" is set to "Run as user"
2. **Redeploy**: Settings changes **require** app redeployment
3. **Clear Browser Cache**: Sometimes cached responses cause stale behavior
4. **Check Databricks Version**: OBO requires recent Databricks workspace versions
5. **View Logs**: Look for the "🔐 AUTHENTICATED AS" section

### No Catalogs Visible?

If OBO is working but you see no catalogs:
- The logged-in user may not have Unity Catalog permissions
- Grant `USE CATALOG` on specific catalogs to the user
- Or grant broader Unity Catalog permissions

## Contact

If you've enabled User Authorization but still don't see the `x-forwarded-access-token` header:
1. Check your Databricks workspace version (OBO requires recent versions)
2. Verify your App is in the Apps workspace (not older App Gallery)
3. Contact Databricks support for OBO enablement issues

## Code Changes Summary

The code now:
- ✅ Detects Databricks Apps environment automatically
- ✅ Checks multiple token header names
- ✅ Provides clear debug output about auth method
- ✅ Shows warning when in Databricks App without OBO
- ✅ Includes instructions to enable User Authorization

