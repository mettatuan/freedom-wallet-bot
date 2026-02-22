# ✅ TESTING CHECKLIST - Web App Setup Flow

**Date:** 20/02/2026  
**Version:** 6-step flow (after login guide fix)  
**Tester:** ___________  
**Bot:** @FreedomWalletBot (local/VPS)

---

## 🎯 TEST CASE 1: NEW USER FULL FLOW

### **Setup:**
- [ ] Fresh Telegram account OR `/reset` command
- [ ] Bot running on: ☐ Local  ☐ VPS
- [ ] Start time: _________

### **A. Registration Flow**

**Step 1: Start Bot**
- [ ] Type `/start`
- [ ] ✅ Receives welcome message
- [ ] ✅ Shows registration buttons
- [ ] Screenshot: [  ]

**Step 2: Complete Registration**
- [ ] Click registration button
- [ ] ✅ Bot asks for Full Name
- [ ] Enter name: ___________
- [ ] ✅ Bot asks for Phone
- [ ] Enter phone: ___________
- [ ] ✅ Bot asks for Email
- [ ] Enter email: ___________
- [ ] ✅ Bot confirms and saves
- [ ] Screenshot: [  ]

**Step 3: Registration Complete**
- [ ] ✅ Sees "Cảm ơn bạn!" message
- [ ] ✅ Wait 1.5 seconds
- [ ] ✅ Receives hu_tien.jpg image
- [ ] ✅ Message explains the system
- [ ] ✅ Shows 2 buttons:
  - [ ] "📋 Tạo Google Sheet"
  - [ ] "❓ Hỏi thêm"
- [ ] Screenshot: [  ]

---

### **B. Web App Setup - 6 Steps**

**BEFORE STARTING:**
- [ ] Prepare Google account to use
- [ ] Have Drive open in browser
- [ ] Ready to follow instructions

---

**Step 1: Copy Template**
- [ ] Click "📋 Tạo Google Sheet"
- [ ] ✅ Bot shows "BƯỚC 1: SAO CHÉP TEMPLATE"
- [ ] ✅ Image shows: make-copy.png
- [ ] ✅ Instructions clear and readable
- [ ] ✅ Shows "📋 Copy Template Link" button
- [ ] ✅ Shows "Tiếp theo ➡️" button
- [ ] ✅ Shows "💬 Cần trợ giúp?" button
- [ ] Screenshot: [  ]

**Actions:**
- [ ] Click "Copy Template Link" button
- [ ] ✅ Link copied to clipboard
- [ ] Paste in browser and open
- [ ] ✅ Google Sheet template opens
- [ ] Click "Make a copy"
- [ ] ✅ Copy created in My Drive
- [ ] Copy URL: ___________________________________

**Verify:**
- [ ] ✅ Template copied successfully
- [ ] ✅ Can see all sheets (Dashboard, Thu_Chi, etc.)

---

**Step 2: Apps Script**
- [ ] Click "Tiếp theo ➡️"
- [ ] ✅ Bot shows "BƯỚC 2: BẬT APPS SCRIPT"
- [ ] ✅ Image shows: app-script.png
- [ ] ✅ Instructions clear
- [ ] ✅ Shows "⬅️ Quay lại" button
- [ ] ✅ Shows "Tiếp theo ➡️" button
- [ ] ✅ Shows "💬 Cần trợ giúp?" button
- [ ] Screenshot: [  ]

**Actions:**
- [ ] Open copied Sheet
- [ ] Go to Extensions > Apps Script
- [ ] ✅ Apps Script editor opens
- [ ] Follow bot instructions to paste code
- [ ] Save Apps Script project

**Verify:**
- [ ] ✅ Apps Script code pasted
- [ ] ✅ Project saved

---

**Step 3: Deploy**
- [ ] Click "Tiếp theo ➡️"
- [ ] ✅ Bot shows "BƯỚC 3: DEPLOY WEB APP"
- [ ] ✅ Image shows: deploy-app.png
- [ ] ✅ Instructions clear
- [ ] ✅ NO authorize instructions here ⚠️
- [ ] ✅ Shows navigation buttons
- [ ] Screenshot: [  ]

**Actions:**
- [ ] In Apps Script, click Deploy > New deployment
- [ ] Select type: Web app
- [ ] Execute as: Me
- [ ] Who has access: Anyone
- [ ] Click "Deploy"
- [ ] ✅ Deployment successful
- [ ] Copy Web App URL
- [ ] Web App URL: ___________________________________

**Verify:**
- [ ] ✅ Got Web App URL
- [ ] ✅ Did NOT open URL yet (wait for Step 4)

---

**Step 4: Login & Authorize** ⭐ **CRITICAL NEW STEP**
- [ ] Click "Tiếp theo ➡️"
- [ ] ✅ Bot shows "BƯỚC 4: MỞ WEB APP & ĐĂNG NHẬP"
- [ ] ✅ Image shows: use-deploy-app.png
- [ ] ✅ Shows navigation buttons
- [ ] Screenshot: [  ]

**Content Verification:**
- [ ] ✅ Title: "🔐 BƯỚC 4: MỞ WEB APP & ĐĂNG NHẬP"
- [ ] ✅ Section: "📋 CÁCH LÀM:"
- [ ] ✅ Instruction 1: "Mở Web App URL (vừa copy ở Bước 3)"
- [ ] ✅ Instruction 2: "Authorize lần đầu:" with 7 sub-steps:
  - [ ] ✅ "Popup 'Authorization required'"
  - [ ] ✅ "Click 'Authorize access'"
  - [ ] ✅ "Chọn tài khoản Google"
  - [ ] ✅ "Thấy 'Google hasn't verified this app'"
  - [ ] ✅ "Click 'Advanced' (Nâng cao)"
  - [ ] ✅ "Click 'Go to [Project name] (unsafe)'"
  - [ ] ✅ "Click 'Allow' (Cho phép)"

- [ ] ✅ Section: "✅ KẾT QUẢ:"
- [ ] ✅ Section: "❓ TẠI SAO 'UNSAFE'?"
  - [ ] ✅ "Không sao! Đây là app CỦA BẠN:"
  - [ ] ✅ "Bạn tự tạo"
  - [ ] ✅ "Dữ liệu trong Drive của bạn"
  - [ ] ✅ "Google chỉ cảnh báo vì chưa verify"
  - [ ] ✅ "100% an toàn!"

- [ ] ✅ Final note: "💡 Sau lần đầu → không cần authorize lại!"

**Actions:**
- [ ] Open Web App URL (from Step 3)
- [ ] ✅ Browser opens Web App
- [ ] ✅ Popup: "Authorization required"
- [ ] Click "Authorize access"
- [ ] ✅ Choose Google account
- [ ] ✅ See "Google hasn't verified this app" warning
- [ ] Click "Advanced" (Nâng cao)
- [ ] ✅ See "Go to [Project name] (unsafe)" link
- [ ] Click it
- [ ] ✅ See permissions list
- [ ] Click "Allow" (Cho phép)
- [ ] ✅ Authorization complete
- [ ] ✅ Web App loads successfully

**Emotional Check:** ⚠️ IMPORTANT
- [ ] Did you feel scared by "unsafe" warning?
  - [ ] ☐ Yes, very scared
  - [ ] ☐ A little worried
  - [ ] ☐ No, guide explained it well

- [ ] Did the explanation help?
  - [ ] ☐ Yes, felt reassured
  - [ ] ☐ Still unsure
  - [ ] ☐ No, still scared

**Verify:**
- [ ] ✅ Web App opened successfully
- [ ] ✅ Can see Freedom Wallet interface
- [ ] ✅ No errors

---

**Step 5: Completion**
- [ ] Click "Tiếp theo ➡️"
- [ ] ✅ Bot shows "BƯỚC 5: HOÀN TẤT!"
- [ ] ✅ Congratulations message
- [ ] ✅ Shows "📘 Tiếp theo: Hướng dẫn sử dụng ➡️" button
- [ ] ✅ Shows "💬 Cần trợ giúp?" button
- [ ] Screenshot: [  ]

---

### **C. Post-Setup Flow**

**Guide Step 0:**
- [ ] Click "📘 Tiếp theo: Hướng dẫn sử dụng ➡️"
- [ ] ✅ Bot shows guide_step_0
- [ ] ✅ Instructions for using the system
- [ ] Screenshot: [  ]

**Complete Setup Guide:**
- [ ] Navigate through all guide steps
- [ ] Total guide steps: _____ steps
- [ ] Last step callback: ___________
- [ ] What happens after guide complete: ___________________

---

## 🎯 TEST CASE 2: HELP LINK VERIFICATION

**Test All Steps:**
- [ ] Step 1: Click "💬 Cần trợ giúp?"
  - [ ] ✅ Opens Telegram chat with @tuanai_mentor
  - [ ] ❌ Should NOT open @freedomwalletapp

- [ ] Step 2: Click "💬 Cần trợ giúp?"
  - [ ] ✅ Opens @tuanai_mentor

- [ ] Step 3: Click "💬 Cần trợ giúp?"
  - [ ] ✅ Opens @tuanai_mentor

- [ ] Step 4: Click "💬 Cần trợ giúp?"
  - [ ] ✅ Opens @tuanai_mentor

- [ ] Step 5: Click "💬 Cần trợ giúp?"
  - [ ] ✅ Opens @tuanai_mentor

**Result:** All help links correct ✅ / Some wrong ❌

---

## 🎯 TEST CASE 3: NAVIGATION

**Forward Navigation:**
- [ ] Step 1 → Step 2: Works ✅ / Fails ❌
- [ ] Step 2 → Step 3: Works ✅ / Fails ❌
- [ ] Step 3 → Step 4: Works ✅ / Fails ❌
- [ ] Step 4 → Step 5: Works ✅ / Fails ❌
- [ ] Step 5 → Guide: Works ✅ / Fails ❌

**Backward Navigation:**
- [ ] Step 5 → Step 4: Works ✅ / Fails ❌
- [ ] Step 4 → Step 3: Works ✅ / Fails ❌
- [ ] Step 3 → Step 2: Works ✅ / Fails ❌
- [ ] Step 2 → Step 1: Works ✅ / Fails ❌

**Skip Test:**
- [ ] Can user skip steps? (try jumping from Step 1 to Step 5)
  - [ ] ☐ Yes (should fix!)
  - [ ] ☐ No (good!)

---

## 🎯 TEST CASE 4: IMAGES

**All Images Load:**
- [ ] Step 1: make-copy.png shows ✅ / missing ❌
- [ ] Step 2: app-script.png shows ✅ / missing ❌
- [ ] Step 3: deploy-app.png shows ✅ / missing ❌
- [ ] Step 4: use-deploy-app.png shows ✅ / missing ❌
- [ ] Step 5: No image (expected) ✅

**Image Quality:**
- [ ] All images clear and readable ✅ / blurry ❌
- [ ] Images match current Google UI ✅ / outdated ❌
- [ ] Images show correct steps ✅ / wrong ❌

---

## 🎯 TEST CASE 5: RETURNING USER

**Setup:**
- [ ] User who completed registration before
- [ ] Type `/start` again

**Expected:**
- [ ] What screen shows? _______________________
- [ ] Does it offer to continue setup? ☐ Yes ☐ No
- [ ] Can access main menu? ☐ Yes ☐ No

---

## 🎯 TEST CASE 6: INTERRUPTED SETUP

**Setup:**
- [ ] Start webapp setup
- [ ] Go to Step 3
- [ ] Close bot (don't complete)
- [ ] Type `/start` again

**Expected:**
- [ ] What shows? _______________________
- [ ] Can resume from Step 3? ☐ Yes ☐ No
- [ ] Has to start from Step 1 again? ☐ Yes ☐ No

---

## 📊 ISSUES FOUND

### **Critical (Must Fix):**
1. ______________________________________
2. ______________________________________
3. ______________________________________

### **High Priority:**
1. ______________________________________
2. ______________________________________
3. ______________________________________

### **Medium Priority:**
1. ______________________________________
2. ______________________________________

### **Low Priority / Nice to Have:**
1. ______________________________________
2. ______________________________________

---

## ⏱️ TIMING

**Total Time:**
- Registration: _____ minutes
- Step 1 (Copy): _____ minutes
- Step 2 (Apps Script): _____ minutes
- Step 3 (Deploy): _____ minutes
- Step 4 (Authorize): _____ minutes  ⭐ Track this!
- Step 5 (Complete): _____ seconds
- Setup Guide: _____ minutes

**Total Setup Time:** _____ minutes

**User Experience:**
- [ ] ☐ Very easy (< 10 min)
- [ ] ☐ Easy (10-15 min)
- [ ] ☐ Moderate (15-20 min)
- [ ] ☐ Difficult (> 20 min)

---

## 💡 USER FEEDBACK (If Real User)

**Clarity (1-5):** ⭐⭐⭐⭐⭐
- [ ] 5 - Very clear, no confusion
- [ ] 4 - Mostly clear, minor questions
- [ ] 3 - Some confusion
- [ ] 2 - Often confused
- [ ] 1 - Very confusing

**Difficulty (1-5):** 
- [ ] 1 - Very easy
- [ ] 2 - Easy
- [ ] 3 - Moderate
- [ ] 4 - Difficult
- [ ] 5 - Very difficult

**Most Confusing Step:**
- Step _____: _______________________________

**Suggestions:**
_________________________________________
_________________________________________
_________________________________________

---

## ✅ SIGN-OFF

**Test Result:**
- [ ] ✅ PASS - All critical tests passed, ready for users
- [ ] ⚠️ PASS WITH ISSUES - Works but has minor issues
- [ ] ❌ FAIL - Critical issues, need fixing

**Tester Signature:** _______________  
**Date:** _______________  
**Time:** _______________

**Next Action:**
- [ ] Deploy to VPS
- [ ] Fix issues first
- [ ] Test again with different account
- [ ] Get real user feedback

---

## 📸 SCREENSHOTS

**Save screenshots of:**
1. Registration complete (hu_tien.jpg message)
2. Step 1 (make-copy.png)
3. Step 2 (app-script.png)
4. Step 3 (deploy-app.png)
5. ⭐ Step 4 (use-deploy-app.png) - MOST IMPORTANT!
6. Step 5 (completion)
7. Guide Step 0

**Screenshot folder:** `docs/test-screenshots/YYYYMMDD/`

---

**Test Version:** 6-step flow (20/02/2026)  
**Changes Tested:** Login guide separation, "unsafe" explanation, help link fix
