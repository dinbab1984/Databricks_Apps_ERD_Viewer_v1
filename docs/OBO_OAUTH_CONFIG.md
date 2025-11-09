# OBO OAuth Configuration Issue

## Current Status

✅ **User Authorization is ENABLED**
✅ **OAuth2 Client ID configured**: `8a4e3f1c-e7e8-4788-967c-338830ec9166`
✅ **Correct scopes configured**:
- `catalog.catalogs:read`
- `catalog.schemas:read`
- `catalog.tables:read`
- `sql`
- `iam.current-user:read`
- `iam.access-control:read`

❌ **BUT: Still getting Service Principal token** (UUID instead of user email)

## The Missing Piece

Even though User Authorization is enabled, the app might still be configured to use the **Service Principal's downscoped token** instead of the **user's OAuth token**.

## What to Check

### Option 1: Look for "Identity Mode" or "Token Type" Setting

In your App Settings, look for additional options like:

1. **Identity Mode**:
   - [ ] Application Identity (uses SP token) ← Current?
   - [x] User Identity (uses user's OAuth token) ← Select this!

2. **Token Type**:
   - [ ] Service Principal token
   - [x] User OAuth token ← Select this!

3. **Run As**:
   - [ ] Application
   - [x] End User ← Select this!

4. **Authentication Method**:
   - [ ] Service Principal
   - [x] OAuth 2.0 (User) ← Select this!

### Option 2: OAuth Redirect URI Configuration

Check if you need to configure **OAuth Redirect URIs** for user authentication:

1. In App Settings, look for **"OAuth Redirect URIs"** or **"Callback URLs"**
2. Your app URL should be listed (e.g., `https://your-app-url.databricks.com/...`)
3. If missing, you may need to add it

### Option 3: User Consent Flow

The issue might be that users need to **explicitly consent** to OAuth access:

1. Check if there's a **"Require user consent"** toggle - it should be ON
2. When users first access the app, they should see an OAuth consent screen
3. Without this, the app falls back to SP credentials

## Databricks Apps Configuration Checklist

Go to your app's configuration and verify ALL of these:

### Authentication Tab:
- [x] User Authorization: **Enabled**
- [ ] **OAuth flow type**: Should be "Authorization Code" or "User OAuth"
- [ ] **Consent required**: Should be enabled
- [ ] **Token audience**: Should be "User" not "Application"

### Advanced Settings (if available):
- [ ] Check for "Use user credentials" or similar toggle
- [ ] Look for "Propagate user identity" setting
- [ ] Check if there's a "User impersonation" option

## Testing the Configuration

### Step 1: Completely Redeploy
1. Save all settings
2. **Stop** the app
3. **Deploy** fresh (not just restart)
4. Wait 2-3 minutes

### Step 2: Clear and Test
1. **Clear browser cache** completely
2. **Open in incognito/private window**
3. You might see an OAuth consent screen (this is good!)
4. Check logs for the authentication type

### Step 3: Check for OAuth Consent Screen

When you access the app, do you see:
- A Databricks OAuth authorization screen?
- A prompt asking to grant permissions to the app?

If **NO**: The app is not using user OAuth, it's using SP credentials.
If **YES**: OAuth is configured, but token isn't being used properly.

## Possible Root Causes

### 1. OAuth Not Fully Enabled
Even though User Authorization shows as enabled, OAuth user flow might not be activated.

**Fix**: Look for additional toggles related to OAuth or user authentication flow.

### 2. Missing OAuth Client Secret
The OAuth client might need a client secret configured.

**Check**: App Settings → look for "OAuth Client Secret" field

### 3. Workspace-Level Setting
Your workspace might have user OAuth disabled at the admin level.

**Check with Admin**: Is user OAuth allowed for apps in this workspace?

### 4. App Type Limitation
Some older Databricks App types might not support full user OAuth.

**Verify**: Is this a modern Databricks App (not legacy App Gallery)?

## What Your App Settings Should Look Like

```
┌─────────────────────────────────────────────┐
│ App Authentication Settings                 │
├─────────────────────────────────────────────┤
│                                             │
│ ☑ User Authorization Enabled                │
│                                             │
│ OAuth Client ID:                            │
│ 8a4e3f1c-e7e8-4788-967c-338830ec9166       │
│                                             │
│ Authentication Mode:                        │
│   ○ Service Principal (App Identity)        │
│   ● User OAuth (User Identity) ← SELECT!    │
│                                             │
│ Token Forwarding:                           │
│   ☑ Include user token in x-forwarded-*     │
│                                             │
│ Scopes: [✓ All configured correctly]       │
│                                             │
└─────────────────────────────────────────────┘
```

## Next Steps for You

1. **Screenshot your FULL authentication settings page**
   - Especially any sections about "identity", "mode", or "token type"

2. **Look for these specific terms in settings:**
   - "User Identity"
   - "Run as user"
   - "OAuth flow"
   - "Token type"
   - "Authentication mode"
   - "Identity propagation"

3. **Check the app logs when a user accesses it:**
   - Does it log an OAuth authorization?
   - Is there a user consent step?

4. **Try accessing from incognito:**
   - Do you get redirected to an OAuth consent page?
   - Or do you go straight to the app?

## Expected Behavior vs Current Behavior

### Current (Wrong):
```
User opens app → No OAuth consent → App uses SP token → UUID in logs
```

### Expected (Correct):
```
User opens app → OAuth consent prompt → User approves → App gets user token → Real email in logs
```

## Contact Databricks Support

If you've checked everything and still can't find the setting, you may need to contact Databricks support with:

1. Your app ID
2. OAuth Client ID: `8a4e3f1c-e7e8-4788-967c-338830ec9166`
3. Question: "How do I configure my app to use user OAuth tokens instead of Service Principal tokens for x-forwarded-access-token header?"

They can verify if:
- User OAuth is enabled for your workspace
- Your app type supports user identity
- There are any additional configuration steps needed

---

**TL;DR**: User Authorization is ON, but there's likely another setting that controls whether to use the **SP's downscoped token** vs the **user's OAuth token**. Look for settings with keywords: "identity mode", "run as", "token type", or "authentication mode".


