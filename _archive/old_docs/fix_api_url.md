# 🔧 Fix API URL - Quick Guide

## ❌ Current Problem

```
Error: HTTP 404
Current URL: https://script.google.com/macros/s/AKfycbyKaRxa56r5plYzjtah0ctT923Irrzlibogg1E0WVj2DgwMP3-kdoWKRJ1sZn2CrT-G/exec
```

**Cause:** Web App deployment không tồn tại hoặc đã expired.

---

## ✅ Solution: Get New Web App URL

### **Step 1: Open Apps Script**

**Method 1: Via clasp**
```bash
cd D:\Projects\FreedomWallet
clasp open
```

**Method 2: Via browser**
- Go to: https://script.google.com/home
- Find project: **Freedom Wallet**

---

### **Step 2: Get Web App URL**

**Option A: Use Existing Deployment (Recommended)**

1. Click **Deploy** (top right)
2. Click **Manage deployments**
3. Find active deployment (Status = "Active")
4. Copy **Web app URL**
5. Should look like: `https://script.google.com/macros/s/AKfycb[UNIQUE_ID]/exec`

**Option B: Create New Deployment**

1. Click **Deploy** → **New deployment**
2. Click gear icon ⚙️ → Select **Web app**
3. Settings:
   ```
   Description: Freedom Wallet API
   Execute as: Me (your email)
   Who has access: Anyone
   ```
4. Click **Deploy**
5. Authorize if needed
6. Copy **Web app URL**

---

### **Step 3: Update .env File**

Edit `D:\Projects\FreedomWalletBot\.env`:

```bash
# Replace with your new URL
FREEDOM_WALLET_API_URL=https://script.google.com/macros/s/YOUR_NEW_DEPLOYMENT_ID/exec
```

---

### **Step 4: Test Connection**

```bash
cd D:\Projects\FreedomWalletBot
python test_cache_performance.py
```

**Expected:**
```
✅ API Key loaded: fwb_bot_te...
✅ Spreadsheet ID: 1er6t9JQHLa9eZ1YTIM4...

📊 Test 1: First balance query (cache miss)
   ✅ Success: 2000-3000ms
   💰 Total Balance: 1,000,000đ
```

---

## 🧪 Quick Test (PowerShell)

```powershell
# Test if URL works
$url = "https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec"
$body = @{
    action = "ping"
    api_key = "fwb_bot_testing_2026"
    spreadsheet_id = "1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg"
} | ConvertTo-Json

Invoke-RestMethod -Uri $url -Method POST -Body $body -ContentType "application/json"
```

**Expected response:**
```json
{
  "success": true,
  "message": "Pong from Bot API!",
  "timestamp": "2026-02-09T14:30:52.123Z"
}
```

---

## 🔍 Common Issues

### Issue 1: Authorization Required

**Symptom:** Redirect to login page

**Fix:**
1. In Apps Script: **Deploy** → **Manage deployments**
2. Click **Edit** (pencil icon)
3. Change "Who has access" to **Anyone**
4. Click **Update**

---

### Issue 2: Still Getting 404

**Symptom:** New URL also returns 404

**Fix:**
1. Deploy file `bot-api-handler-vietnamese.gs` phải tồn tại trong project
2. Run `clasp push` to upload latest code:
   ```bash
   cd D:\Projects\FreedomWallet
   clasp push
   ```
3. Redeploy Web App

---

### Issue 3: Multiple Deployments Confused

**Symptom:** Có nhiều deployments, không biết dùng cái nào

**Fix:**
1. **Manage deployments**
2. **Archive** tất cả deployments cũ (nút 3 chấm → Archive)
3. Tạo 1 deployment mới duy nhất
4. Use that URL

---

## ✅ Verification Checklist

After updating URL:

```
□ URL copied correctly (no spaces, complete /exec)
□ .env file saved
□ Test with PowerShell → Success
□ Test with Python → Success
□ Bot can ping API → Success
```

---

## 📞 Need Current Deployment ID?

Nếu bạn cần tôi giúp lấy deployment ID hiện tại:

1. Share screenshot of **Manage deployments** page
2. Hoặc run this in Apps Script:
   ```javascript
   function getCurrentDeploymentUrl() {
     Logger.log(ScriptApp.getService().getUrl());
   }
   ```
3. Check logs → Copy URL
