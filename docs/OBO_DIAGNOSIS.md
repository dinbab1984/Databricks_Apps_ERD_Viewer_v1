# OBO Diagnosis - OAuth Authorized but Still Using SP Token

## Current Situation

✅ OAuth consent page appeared  
✅ User authorized the app  
✅ `X-Forwarded-Access-Token` header exists  
❌ **Token is still Service Principal's token (UUID email)**  

## Critical Check: User Email Headers

The enhanced debug will now show `X-Forwarded-Email` and `X-Forwarded-User` values.

### If these headers show:
- **UUID** (like `c77f1610-9bc8-41b1-9518-e117f6450feb`) → Still using SP
- **Real email** (like `john.doe@company.com`) → OAuth IS working but token extraction failed

## Diagnostic Questions

### 1. After OAuth Authorization, Did You...?

- [ ] **Refresh the page?** (Not enough)
- [ ] **Restart the app?** (Still not enough)
- [ ] **Stop and Start the app?** (Might be needed)
- [ ] **Redeploy the app?** (Most likely needed)

**Action:** Try a **complete cold restart**:
```bash
# Stop the app
databricks apps stop <app-name>

# Wait 30 seconds

# Start fresh
databricks apps start <app-name>
```

### 2. OAuth Scopes - Are They Actually Applied?

You configured these scopes:
- `catalog.catalogs:read`
- `catalog.schemas:read`  
- `catalog.tables:read`
- `sql`

But did you **save AND redeploy** after adding them?

**Action:** In App Settings → User Authorization:
1. Verify ALL scopes are listed
2. Click "Save"
3. **Redeploy the entire app** (not just restart)

### 3. Is OAuth Client Using Correct Flow?

**Check:** In your OAuth Client settings, look for:
- **Grant Type**: Should be "Authorization Code" (user flow)
- **Not**: "Client Credentials" (SP flow)

**Action:** If it shows "Client Credentials":
1. Delete and recreate the OAuth client
2. Ensure it's configured for "Authorization Code" flow
3. Redeploy

### 4. App Configuration File

**Check** if you have an `app.yaml` or `databricks.yml` file with:

```yaml
resources:
  apps:
    erd_viewer:
      config:
        auth:
          type: oauth_user  # ← Should be this
          # NOT: service_principal
```

**Action:** If missing or wrong:
1. Update the config file
2. Redeploy via `databricks bundle deploy`

## Expected Debug Output (After Fix)

### What You Should See:

```
DEBUG SIDEBAR: X-Forwarded-Email = john.doe@company.com  ← Real email!
DEBUG SIDEBAR: X-Forwarded-User = john.doe@company.com

DEBUG OBO: X-Forwarded-Access-Token = eyJraWQiOi... (length=1234)

🔐 AUTHENTICATED AS:
   Type: USER ✅
   Email: john.doe@company.com  ← Not a UUID!

✅✅✅ OBO IS WORKING CORRECTLY! ✅✅✅
```

### What You're Currently Seeing:

```
DEBUG SIDEBAR: X-Forwarded-Email = c77f1610-9bc8-41b1-9518-e117f6450feb  ← UUID!

🔐 AUTHENTICATED AS:
   Type: SERVICE PRINCIPAL ⚠️
   SP UUID: c77f1610-9bc8-41b1-9518-e117f6450feb
```

## Hypothesis: OAuth Permission ≠ OAuth Token

You may have:
1. ✅ **Granted OAuth permission** (consent page)
2. ❌ **But app runtime is still configured to use SP token**

The OAuth authorization just gave the app **permission** to request user tokens.
But the app **configuration** determines whether it actually **uses** those tokens.

## Most Likely Solution

Based on similar Databricks Apps issues, the most common fix is:

### Complete App Restart After OAuth Configuration

1. **Go to Databricks Apps Console**
2. **Stop your app completely**
3. Wait 60 seconds for full shutdown
4. **Start the app** (cold start)
5. Access the app in a **new incognito window**
6. Check if you need to re-authorize (you might!)
7. After authorization, check the logs

### If Still Not Working: Redeploy

The OAuth client registration might need the app to be redeployed:

```bash
# Complete redeployment
databricks apps deploy <app-name> --force

# Or via UI:
# Apps → Your App → Actions → Redeploy
```

## Alternative: Check Databricks Workspace Settings

Someone with workspace admin access should verify:

1. **Workspace Settings** → **Advanced** → **Apps**
2. Look for: "Allow apps to use user OAuth tokens"
3. Ensure this is **enabled** (not just the preview feature)

There might be TWO settings:
- ☑ Enable OBO User Authorization (Preview) ← You enabled this
- ☐ **Allow apps to propagate user OAuth tokens** ← Might need this too!

## Next Steps

1. **Run the app again with enhanced debug**
   - Look for `X-Forwarded-Email` value (UUID vs real email)
   
2. **Try complete app restart**
   - Stop → Wait → Start → Test

3. **If still UUID, check for additional workspace settings**
   - Ask admin to verify all OAuth/OBO settings

4. **Share the complete debug output** including:
   - `X-Forwarded-Email` value
   - `X-Forwarded-User` value  
   - Total number of headers
   - Any cookie-related information

---

**Current Status**: OAuth authorized but token still belongs to SP  
**Next Action**: Check X-Forwarded-Email header value + try complete app restart


