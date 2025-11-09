# OBO Quick Fix - Run as App vs Run as User

## 🔴 The Problem You're Experiencing

Your debug output shows:
```
Type: USER ✅
Email: c77f1610-9bc8-41b1-9518-e117f6450feb
```

**That UUID is NOT a user email - it's the Service Principal's identifier!**

## ❌ What's Wrong

1. ✅ OBO header is present: `x-forwarded-access-token`
2. ✅ Token is being extracted (length 976)
3. ✅ Token is being used by the app
4. ❌ **BUT the token belongs to the Service Principal, NOT the user**

## 🎯 Root Cause

Your Databricks App authentication is set to:
- **"Run as app"** ❌ (Current - WRONG)

Instead of:
- **"Run as user"** ✅ (Target - CORRECT)

## 🔧 The Fix (Step by Step)

### Step 1: Open App Settings
1. Go to Databricks Workspace
2. Navigate to **Apps** section
3. Find your ERD Viewer app
4. Click on the app name
5. Click **"Settings"** or **"Configure"**

### Step 2: Find Authentication Settings
Look for one of these sections:
- **"Authentication"**
- **"User Authorization"**
- **"Run as"**
- **"Execution Mode"**

### Step 3: Change the Setting
You'll see something like:

**Option A**: Toggle switch
```
☐ Run as user
☑ Run as app  ← Currently selected (WRONG)
```
**Change to:**
```
☑ Run as user  ← Select this!
☐ Run as app
```

**Option B**: Dropdown menu
```
Run as: [App ▼]  ← Currently selected (WRONG)
```
**Change to:**
```
Run as: [User ▼]  ← Select this!
```

**Option C**: Radio buttons
```
○ Run as application (Service Principal)  ← Currently selected (WRONG)
● Run as user  ← Select this!
```

### Step 4: Save and Redeploy
1. Click **"Save"** or **"Update"**
2. **IMPORTANT**: Click **"Redeploy"** or **"Restart App"**
3. Wait for deployment to complete (~30-60 seconds)
4. Refresh your browser

### Step 5: Verify the Fix
After redeployment, check the logs. You should now see:

```
🔐 AUTHENTICATED AS:
   Type: USER ✅
   Email: your.actual.email@company.com  ← Real email, not UUID!

✅✅✅ OBO IS WORKING CORRECTLY! ✅✅✅
```

## 📊 Before vs After

### Before (Current - WRONG):
```
Email: c77f1610-9bc8-41b1-9518-e117f6450feb  ← UUID = Service Principal
```
- All users see the same catalogs (SP's catalogs)
- All users have the same permissions (SP's permissions)
- Audit logs show the Service Principal name

### After (Target - CORRECT):
```
Email: john.doe@company.com  ← Real email!
```
- Each user sees their own accessible catalogs
- Each user has their own permissions
- Audit logs show the actual user names

## 🔍 How to Verify It's Working

1. **Check the logs for this section:**
   ```
   ============================================================
   🔐 AUTHENTICATED AS:
      Type: USER ✅
      Email: <should be real email, not UUID>
   
   ✅✅✅ OBO IS WORKING CORRECTLY! ✅✅✅
   ============================================================
   ```

2. **Test with two different users:**
   - User A with access to Catalog X
   - User B without access to Catalog X
   - They should see different catalogs!

3. **Check Unity Catalog audit logs:**
   - Should show actual usernames, not Service Principal name

## ❓ Can't Find the Setting?

If you can't find the "Run as user" option:

1. **Check your Databricks version**: OBO requires recent versions
2. **Verify app type**: Must be a Databricks App (not App Gallery)
3. **Check permissions**: You need admin access to modify app settings
4. **Look for**: "User Authorization", "OBO", "On-Behalf-Of", or "Identity Propagation"

## 📞 Still Not Working?

If you've changed to "Run as user" and redeployed, but still see a UUID:

1. **Clear browser cache** and try again
2. **Wait 5 minutes** for settings to propagate
3. **Check if User Authorization is enabled** at the workspace level
4. **Contact your Databricks admin** - there may be workspace-level restrictions

## 🎉 Success Criteria

You'll know it's working when:
- ✅ Email is a real email address (not a UUID)
- ✅ Type shows "USER ✅"
- ✅ Message says "OBO IS WORKING CORRECTLY"
- ✅ Different users see different catalogs based on their permissions

---

**Current Status**: Your app is configured to "Run as app" 
**Action Required**: Change to "Run as user" in App Settings


