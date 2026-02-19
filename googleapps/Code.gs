/**
 * ============================================
 * FREEDOM WALLET - REGISTRATION BACKEND
 * Google Apps Script - Production Version
 * ============================================
 * 
 * Xử lý đăng ký từ Landing Page: freedom-wallet-landing
 * 
 * Features:
 * - Thu thập đăng ký FREE và Premium
 * - Lưu vào Google Sheets
 * - Kiểm tra duplicate
 * - Hỗ trợ referral tracking
 * 
 * Created: 2026-02-06
 */

// ============================================
// CONFIGURATION
// ============================================

const CONFIG = {
  SHEET_NAME: 'FreedomWallet_Registrations',
  DEFAULT_STATUS: 'Đã đăng ký',
  TIMEZONE: 'Asia/Ho_Chi_Minh',
  
  // Column mapping (0-based index)
  COLUMNS: {
    DATE: 0,        // A: 📅 Ngày đăng ký
    USER_ID: 1,     // B: User ID (Telegram)
    USERNAME: 2,    // C: Username (Telegram @username)
    NAME: 3,        // D: Họ & Tên
    EMAIL: 4,       // E: 📧 Email
    PHONE: 5,       // F: 👤 Điện thoại
    PLAN: 6,        // G: 💎 Gói
    REFERRAL_CODE: 7,  // H: 🔗 Link giới thiệu
    REFERRAL_COUNT: 8, // I: 👥 Số người đã giới thiệu
    SOURCE: 9,      // J: 📍 Nguồn
    STATUS: 10,     // K: 📊 Trạng thái
    REFERRER: 11    // L: 👤 Người giới thiệu
  },
  
  // Column headers
  HEADERS: [
    '📅 Ngày đăng ký',
    'User ID',
    'Username',
    'Họ & Tên',
    '📧 Email',
    '👤 Điện thoại',
    '💎 Gói',
    '🔗 Link giới thiệu',
    '👥 Số người đã giới thiệu',
    '📍 Nguồn',
    '📊 Trạng thái',
    '👤 Người giới thiệu'
  ],
  
  // Plan types
  PLANS: {
    FREE: 'FREE',
    PREMIUM: 'Premium'
  },
  
  // Status types
  STATUS: {
    REGISTERED: 'Đã đăng ký',
    PENDING_PAYMENT: 'Chờ thanh toán',
    PAID: 'Đã thanh toán',
    CONFIRMED: 'Đã xác nhận',
    UPGRADED_REFERRAL: 'Nâng cấp FREE (Giới thiệu)'
  }
};

// ============================================
// MAIN HANDLERS
// ============================================

/**
 * Handle GET requests - Test endpoint
 */
function doGet(e) {
  try {
    const params = e.parameter || {};
    
    // Handle Kanban requests
    if (params.action === 'getFeatures') {
      return handleKanbanGetRequests(params);
    }
    
    // Test endpoint
    if (params.test) {
      return createJsonResponse(true, 'Freedom Wallet API is working!', {
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        sheetName: CONFIG.SHEET_NAME
      });
    }
    
    // Get registrations count
    const sheet = getOrCreateSheet();
    const totalRegistrations = sheet.getLastRow() - 1; // Exclude header
    
    return createJsonResponse(true, 'Sheet info retrieved', {
      totalRegistrations: totalRegistrations,
      sheetName: sheet.getName(),
      spreadsheetId: SpreadsheetApp.getActiveSpreadsheet().getId()
    });
    
  } catch (error) {
    logError('doGet', error);
    return createJsonResponse(false, 'Server error: ' + error.message);
  }
}

/**
 * Handle OPTIONS requests (CORS preflight)
 * Google Apps Script requires this for cross-origin requests
 */
function doOptions(e) {
  return ContentService
    .createTextOutput('')
    .setMimeType(ContentService.MimeType.TEXT);
}

/**
 * Handle POST requests - Add new registration
 */
function doPost(e) {
  try {
    // Parse request data
    const data = parseRequestData(e);
    
    // Handle Kanban requests
    if (data.action === 'addFeature' || data.action === 'voteFeature') {
      return handleKanbanPostRequests(data);
    }
    
    logInfo('doPost', `Received registration: ${JSON.stringify(data)}`);
    
    // Validate input
    const validation = validateInput(data);
    if (!validation.valid) {
      return createJsonResponse(false, validation.message);
    }
    
    // Check for duplicates
    const duplicate = checkDuplicate(data.email, data.phone);
    if (duplicate.exists) {
      return createJsonResponse(false, duplicate.message, {
        duplicate: true,
        existingRow: duplicate.row
      });
    }
    
    // Add to sheet
    const result = addRegistration(data);
    
    if (result.success) {
      const sheet = getOrCreateSheet();
      const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
      
      return createJsonResponse(true, 'Đăng ký thành công! 🎉', {
        rowNumber: result.rowNumber,
        referralCode: result.referralCode,
        plan: data.plan,
        message: data.plan === CONFIG.PLANS.PREMIUM 
          ? 'Vui lòng chuyển khoản để hoàn tất đăng ký.' 
          : 'Chào mừng bạn đến với Freedom Wallet!',
        spreadsheetUrl: spreadsheet.getUrl()
      });
    } else {
      return createJsonResponse(false, 'Không thể lưu dữ liệu: ' + result.error);
    }
    
  } catch (error) {
    logError('doPost', error);
    return createJsonResponse(false, 'Lỗi hệ thống: ' + error.message);
  }
}

// ============================================
// CORE FUNCTIONS
// ============================================

/**
 * Get or create sheet with proper headers
 */
function getOrCreateSheet() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = spreadsheet.getSheetByName(CONFIG.SHEET_NAME);
  
  // Create sheet if not exists
  if (!sheet) {
    sheet = spreadsheet.insertSheet(CONFIG.SHEET_NAME);
    
    // Set headers
    const headerRange = sheet.getRange(1, 1, 1, CONFIG.HEADERS.length);
    headerRange.setValues([CONFIG.HEADERS]);
    
    // Format headers
    headerRange
      .setFontWeight('bold')
      .setBackground('#0F50AD')
      .setFontColor('#ffffff')
      .setHorizontalAlignment('center')
      .setVerticalAlignment('middle');
    
    // Set header height
    sheet.setRowHeight(1, 40);
    
    // Freeze header row
    sheet.setFrozenRows(1);
    
    // Set column widths
    sheet.setColumnWidth(1, 150);  // Date
    sheet.setColumnWidth(2, 200);  // Name
    sheet.setColumnWidth(3, 220);  // Email
    sheet.setColumnWidth(4, 120);  // Phone
    sheet.setColumnWidth(5, 100);  // Plan
    sheet.setColumnWidth(6, 150);  // Referral Code
    sheet.setColumnWidth(7, 100);  // Referral Count
    sheet.setColumnWidth(8, 150);  // Source
    sheet.setColumnWidth(9, 150);  // Status
    sheet.setColumnWidth(10, 150); // Referrer
    
    logInfo('getOrCreateSheet', `Created new sheet: ${CONFIG.SHEET_NAME}`);
  }
  
  return sheet;
}

/**
 * Parse request data from POST
 */
function parseRequestData(e) {
  try {
    if (!e || !e.postData) {
      throw new Error('No POST data received');
    }
    
    const contentType = e.postData.type;
    const rawContent = e.postData.contents;
    let data;
    
    logInfo('parseRequestData', `Content-Type: ${contentType}`);
    
    // Try to parse as JSON first
    try {
      data = JSON.parse(rawContent);
      logInfo('parseRequestData', 'Parsed as JSON');
    } catch (parseError) {
      // If JSON parsing fails, try form data
      if (e.parameter) {
        data = e.parameter;
        logInfo('parseRequestData', 'Parsed as FormData');
      } else {
        throw new Error('Unable to parse request data');
      }
    }
    
    // Normalize and return data
    return {
      fullName: (data.fullName || data.name || '').trim(),
      email: (data.email || '').trim().toLowerCase(),
      phone: (data.phone || '').trim(),
      plan: (data.plan || CONFIG.PLANS.FREE).trim().toLowerCase(),
      source: (data.source || 'Landing Page').trim(),
      referralCode: (data.referralCode || '').trim(),
      referrer: (data.referrer || data.ref || '').trim()
    };
    
  } catch (error) {
    logError('parseRequestData', error);
    throw new Error('Failed to parse request: ' + error.message);
  }
}

/**
 * Validate input data
 */
function validateInput(data) {
  // Check full name
  if (!data.fullName || data.fullName.length < 2) {
    return { valid: false, message: 'Vui lòng nhập họ tên (tối thiểu 2 ký tự)' };
  }
  
  // Check email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!data.email || !emailRegex.test(data.email)) {
    return { valid: false, message: 'Email không hợp lệ' };
  }
  
  // Check phone format (Vietnamese phone numbers)
  const phoneRegex = /^(0|\+84)[0-9]{9,10}$/;
  if (!data.phone || !phoneRegex.test(data.phone.replace(/\s/g, ''))) {
    return { valid: false, message: 'Số điện thoại không hợp lệ (VD: 0901234567)' };
  }
  
  // Check plan
  const planNormalized = data.plan.toLowerCase();
  if (planNormalized !== 'free' && planNormalized !== 'premium') {
    return { valid: false, message: 'Gói không hợp lệ. Vui lòng chọn FREE hoặc Premium' };
  }
  
  return { valid: true };
}

/**
 * Check for duplicate registrations
 */
function checkDuplicate(email, phone) {
  try {
    const sheet = getOrCreateSheet();
    const lastRow = sheet.getLastRow();
    
    if (lastRow <= 1) {
      return { exists: false };
    }
    
    // Get all data
    const dataRange = sheet.getRange(2, 1, lastRow - 1, CONFIG.HEADERS.length);
    const data = dataRange.getValues();
    
    // Check for duplicate email or phone
    for (let i = 0; i < data.length; i++) {
      const row = data[i];
      const rowEmail = row[CONFIG.COLUMNS.EMAIL];
      const rowPhone = row[CONFIG.COLUMNS.PHONE];
      
      if (rowEmail === email) {
        return {
          exists: true,
          message: 'Email này đã được đăng ký. Vui lòng kiểm tra email hoặc liên hệ hỗ trợ.',
          row: i + 2
        };
      }
      
      if (rowPhone === phone) {
        return {
          exists: true,
          message: 'Số điện thoại này đã được đăng ký. Vui lòng kiểm tra lại.',
          row: i + 2
        };
      }
    }
    
    return { exists: false };
    
  } catch (error) {
    logError('checkDuplicate', error);
    return { exists: false }; // Allow registration if check fails
  }
}

/**
 * Add registration to sheet
 */
function addRegistration(data) {
  try {
    const sheet = getOrCreateSheet();
    
    // Normalize plan name
    const planDisplay = data.plan.toLowerCase() === 'premium' 
      ? CONFIG.PLANS.PREMIUM 
      : CONFIG.PLANS.FREE;
    
    // Determine status based on plan
    const status = planDisplay === CONFIG.PLANS.PREMIUM 
      ? CONFIG.STATUS.PENDING_PAYMENT 
      : CONFIG.STATUS.REGISTERED;
    
    // Format date
    const timestamp = Utilities.formatDate(
      new Date(), 
      CONFIG.TIMEZONE, 
      'dd/MM/yyyy HH:mm:ss'
    );
    
    // Prepare row data (12 columns now)
    const rowData = [
      timestamp,              // A: Date
      data.userId || '',      // B: User ID (Telegram ID)
      data.username || '',    // C: Username (@username)
      data.fullName,          // D: Name
      data.email,             // E: Email
      data.phone,             // F: Phone
      planDisplay,            // G: Plan
      data.referralCode || '', // H: Referral Code
      0,                      // I: Referral Count (initial)
      data.source,            // J: Source
      status,                 // K: Status
      data.referrer || ''     // L: Referrer
    ];
    
    // Append to sheet
    const newRow = sheet.getLastRow() + 1;
    sheet.getRange(newRow, 1, 1, rowData.length).setValues([rowData]);
    
    // Format the new row
    formatNewRow(sheet, newRow, planDisplay);
    
    logInfo('addRegistration', `Added row ${newRow}: ${data.fullName} - ${planDisplay}`);
    
    // If user was referred, increment referrer's count
    if (data.referrer) {
      incrementReferralCount(data.referrer);
    }
    
    return {
      success: true,
      rowNumber: newRow,
      referralCode: data.referralCode
    };
    
  } catch (error) {
    logError('addRegistration', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Format new row based on plan
 */
function formatNewRow(sheet, rowNumber, plan) {
  try {
    const range = sheet.getRange(rowNumber, 1, 1, CONFIG.HEADERS.length);
    
    // Alternating row colors for readability
    const bgColor = rowNumber % 2 === 0 ? '#f8f9fa' : '#ffffff';
    range.setBackground(bgColor);
    
    // Highlight Premium plans
    if (plan === CONFIG.PLANS.PREMIUM) {
      const planCell = sheet.getRange(rowNumber, CONFIG.COLUMNS.PLAN + 1);
      planCell
        .setBackground('#FFF9E6')
        .setFontWeight('bold')
        .setFontColor('#E5A21B');
    }
    
    // Bold name column
    const nameCell = sheet.getRange(rowNumber, CONFIG.COLUMNS.NAME + 1);
    nameCell.setFontWeight('bold');
    
    // Align columns
    range.setVerticalAlignment('middle');
    sheet.getRange(rowNumber, CONFIG.COLUMNS.DATE + 1).setHorizontalAlignment('center');
    sheet.getRange(rowNumber, CONFIG.COLUMNS.PLAN + 1).setHorizontalAlignment('center');
    sheet.getRange(rowNumber, CONFIG.COLUMNS.STATUS + 1).setHorizontalAlignment('center');
    
  } catch (error) {
    logError('formatNewRow', error);
  }
}

/**
 * Increment referral count for a referrer
 */
function incrementReferralCount(referrerCode) {
  try {
    const sheet = getOrCreateSheet();
    const lastRow = sheet.getLastRow();
    
    if (lastRow <= 1) return;
    
    const dataRange = sheet.getRange(2, 1, lastRow - 1, CONFIG.HEADERS.length);
    const data = dataRange.getValues();
    
    for (let i = 0; i < data.length; i++) {
      const referralCode = data[i][CONFIG.COLUMNS.REFERRAL_CODE];
      
      if (referralCode === referrerCode) {
        const rowNumber = i + 2;
        const countCell = sheet.getRange(rowNumber, CONFIG.COLUMNS.REFERRAL_COUNT + 1);
        const currentCount = countCell.getValue() || 0;
        const newCount = currentCount + 1;
        
        countCell.setValue(newCount);
        
        // Check if user reached 2 referrals (auto-upgrade)
        if (newCount >= 2) {
          const statusCell = sheet.getRange(rowNumber, CONFIG.COLUMNS.STATUS + 1);
          statusCell.setValue(CONFIG.STATUS.UPGRADED_REFERRAL);
          
          // Highlight the row
          const rowRange = sheet.getRange(rowNumber, 1, 1, CONFIG.HEADERS.length);
          rowRange.setBackground('#E6F9F0');
          
          logInfo('incrementReferralCount', `User ${referralCode} reached 2 referrals - auto upgraded!`);
        }
        
        logInfo('incrementReferralCount', `Incremented count for ${referrerCode}: ${newCount}`);
        return;
      }
    }
    
  } catch (error) {
    logError('incrementReferralCount', error);
  }
}

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Create JSON response
 * Note: Google Apps Script handles CORS automatically when deployed as "Anyone" access
 */
function createJsonResponse(success, message, data = null) {
  const response = {
    success: success,
    message: message,
    timestamp: new Date().toISOString()
  };
  
  if (data) {
    response.data = data;
  }
  
  return ContentService
    .createTextOutput(JSON.stringify(response))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Log info message
 */
function logInfo(functionName, message) {
  console.log(`[INFO][${functionName}] ${message}`);
}

/**
 * Log error message
 */
function logError(functionName, error) {
  console.error(`[ERROR][${functionName}] ${error.message || error}`);
  console.error(error.stack);
}

// ============================================
// UTILITY FUNCTIONS FOR MANUAL MANAGEMENT
// ============================================

/**
 * Update status of a registration by email
 * Can be called manually from Apps Script editor
 */
function updateStatusByEmail(email, newStatus) {
  try {
    const sheet = getOrCreateSheet();
    const lastRow = sheet.getLastRow();
    
    if (lastRow <= 1) {
      return { success: false, message: 'No registrations found' };
    }
    
    const dataRange = sheet.getRange(2, 1, lastRow - 1, CONFIG.HEADERS.length);
    const data = dataRange.getValues();
    
    for (let i = 0; i < data.length; i++) {
      if (data[i][CONFIG.COLUMNS.EMAIL] === email.toLowerCase()) {
        const rowNumber = i + 2;
        sheet.getRange(rowNumber, CONFIG.COLUMNS.STATUS + 1).setValue(newStatus);
        
        logInfo('updateStatusByEmail', `Updated row ${rowNumber}: ${email} -> ${newStatus}`);
        return { 
          success: true, 
          message: `Updated status for ${email}`,
          row: rowNumber 
        };
      }
    }
    
    return { success: false, message: `Email ${email} not found` };
    
  } catch (error) {
    logError('updateStatusByEmail', error);
    return { success: false, message: error.message };
  }
}

/**
 * Count registrations by plan
 * Can be called manually from Apps Script editor
 */
function getRegistrationStats() {
  try {
    const sheet = getOrCreateSheet();
    const lastRow = sheet.getLastRow();
    
    if (lastRow <= 1) {
      return { free: 0, premium: 0, total: 0 };
    }
    
    const planColumn = sheet.getRange(2, CONFIG.COLUMNS.PLAN + 1, lastRow - 1, 1).getValues();
    
    let freeCount = 0;
    let premiumCount = 0;
    
    for (let i = 0; i < planColumn.length; i++) {
      const plan = planColumn[i][0];
      if (plan === CONFIG.PLANS.FREE) {
        freeCount++;
      } else if (plan === CONFIG.PLANS.PREMIUM) {
        premiumCount++;
      }
    }
    
    const stats = {
      free: freeCount,
      premium: premiumCount,
      total: freeCount + premiumCount,
      limit: 1000,
      remaining: Math.max(0, 1000 - freeCount)
    };
    
    Logger.log(JSON.stringify(stats, null, 2));
    return stats;
    
  } catch (error) {
    logError('getRegistrationStats', error);
    return null;
  }
}

/**
 * Initialize or reset sheet (CAREFUL - deletes data!)
 * Uncomment and run manually if needed
 */
// function resetSheet() {
//   const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
//   const sheet = spreadsheet.getSheetByName(CONFIG.SHEET_NAME);
//   
//   if (sheet) {
//     spreadsheet.deleteSheet(sheet);
//   }
//   
//   getOrCreateSheet();
//   Logger.log('Sheet reset complete');
// }
// */  // ← Fixed: commented out extra closing tag

// ============================================
// KANBAN CONFIGURATION
// ============================================

const KANBAN_CONFIG = {
  FEATURES_SHEET: 'Roadmap_Features',
  VOTES_SHEET: 'Feature_Votes',
  
  // Features sheet columns (0-based)
  FEATURES_COLUMNS: {
    ID: 0,           // A: ID (unique)
    TIMESTAMP: 1,    // B: Timestamp
    EMAIL: 2,        // C: Email người đề xuất
    TITLE: 3,        // D: Tên tính năng
    DESCRIPTION: 4,  // E: Mô tả
    TYPE: 5,         // F: Loại (FEATURE/IMPROVEMENT/BUGFIX)
    STATUS: 6,       // G: Trạng thái (TODO/IN PROGRESS/IN REVIEW/DONE)
    VOTES: 7         // H: Số vote
  },
  
  FEATURES_HEADERS: [
    'ID',
    'Timestamp',
    'Email',
    'Title',
    'Description',
    'Type',
    'Status',
    'Votes'
  ],
  
  // Votes sheet columns
  VOTES_COLUMNS: {
    TIMESTAMP: 0,    // A: Timestamp
    FEATURE_ID: 1,   // B: Feature ID
    EMAIL: 2         // C: Email người vote
  },
  
  VOTES_HEADERS: [
    'Timestamp',
    'Feature ID',
    'Email'
  ],
  
  TYPES: {
    FEATURE: 'FEATURE',
    IMPROVEMENT: 'IMPROVEMENT',
    BUGFIX: 'BUGFIX'
  },
  
  STATUSES: {
    BACKLOG: 'BACKLOG',
    TODO: 'TODO',
    IN_DEVELOPMENT: 'IN DEVELOPMENT',
    DONE: 'DONE'
  }
};

// ============================================
// SHEET HELPERS FOR KANBAN
// ============================================

/**
 * Get or create Features sheet
 */
function getOrCreateFeaturesSheet() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = spreadsheet.getSheetByName(KANBAN_CONFIG.FEATURES_SHEET);
  
  if (!sheet) {
    sheet = spreadsheet.insertSheet(KANBAN_CONFIG.FEATURES_SHEET);
    
    // Set headers
    const headerRange = sheet.getRange(1, 1, 1, KANBAN_CONFIG.FEATURES_HEADERS.length);
    headerRange.setValues([KANBAN_CONFIG.FEATURES_HEADERS]);
    headerRange.setFontWeight('bold');
    headerRange.setBackground('#4285F4');
    headerRange.setFontColor('#FFFFFF');
    
    // Format columns
    sheet.setColumnWidth(1, 120);  // ID
    sheet.setColumnWidth(2, 150);  // Timestamp
    sheet.setColumnWidth(3, 200);  // Email
    sheet.setColumnWidth(4, 250);  // Title
    sheet.setColumnWidth(5, 400);  // Description
    sheet.setColumnWidth(6, 120);  // Type
    sheet.setColumnWidth(7, 120);  // Status
    sheet.setColumnWidth(8, 80);   // Votes
    
    // Freeze header row
    sheet.setFrozenRows(1);
    
    Logger.log('✅ Created Features sheet');
    
    // Add sample features
    addSampleFeatures(sheet);
  }
  
  return sheet;
}

/**
 * Get or create Votes sheet
 */
function getOrCreateVotesSheet() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = spreadsheet.getSheetByName(KANBAN_CONFIG.VOTES_SHEET);
  
  if (!sheet) {
    sheet = spreadsheet.insertSheet(KANBAN_CONFIG.VOTES_SHEET);
    
    // Set headers
    const headerRange = sheet.getRange(1, 1, 1, KANBAN_CONFIG.VOTES_HEADERS.length);
    headerRange.setValues([KANBAN_CONFIG.VOTES_HEADERS]);
    headerRange.setFontWeight('bold');
    headerRange.setBackground('#34A853');
    headerRange.setFontColor('#FFFFFF');
    
    // Format columns
    sheet.setColumnWidth(1, 150);  // Timestamp
    sheet.setColumnWidth(2, 120);  // Feature ID
    sheet.setColumnWidth(3, 200);  // Email
    
    // Freeze header row
    sheet.setFrozenRows(1);
    
    Logger.log('✅ Created Votes sheet');
  }
  
  return sheet;
}

/**
 * Add sample features for demo
 * Updated 2026-02-16: Now using REAL features from changelog.md
 */
function addSampleFeatures(sheet) {
  const samples = [
    // ============================================
    // DONE - Completed features from changelog.md
    // ============================================
    ['FW_V3.2.1', '2026-01-16T00:00:00Z', 'admin@freedomwallet.app', 'v3.2.1: Mobile Asset Price Updates', 'Sửa lỗi cập nhật giá tài sản trên mobile, validation ngày mua format DD/MM/YYYY', 'BUGFIX', 'DONE', 0],
    ['FW_V3.2.0', '2026-01-15T00:00:00Z', 'admin@freedomwallet.app', 'v3.2.0: Core Infrastructure', 'Constants, Logger, ErrorHandler modules + API caching + 12 module updates', 'FEATURE', 'DONE', 0],
    ['FW_V3.1.0', '2026-01-15T00:00:00Z', 'admin@freedomwallet.app', 'v3.1.0: Cache System & 6 Jars', 'Multi-level cache (Script/User/Doc), Jars popup, DebtsSyncOptimizer, account filters', 'FEATURE', 'DONE', 0],
    ['FW_V3.0.0', '2025-11-01T00:00:00Z', 'admin@freedomwallet.app', 'v3.0.0: Major Modules', 'Assets, Investments, Debts, 6 Jars, Dashboard - các module chính hoàn chỉnh', 'FEATURE', 'DONE', 0],
    ['FW_V2.0.0', '2025-08-01T00:00:00Z', 'admin@freedomwallet.app', 'v2.0.0: Transactions CRUD', 'Module giao dịch cơ bản với CRUD operations đầy đủ', 'FEATURE', 'DONE', 0],
    ['FW_BOT_V1', '2026-01-10T00:00:00Z', 'admin@freedomwallet.app', 'Telegram Bot v1.0', 'Bot hỗ trợ 24/7 với GPT-4, knowledge base, tutorials, troubleshooting, 6 Jars tips', 'FEATURE', 'DONE', 0],
    
    // ============================================
    // IN DEVELOPMENT - Currently being developed
    // ============================================
    ['FW001', '2026-02-10T00:00:00Z', 'admin@freedomwallet.app', 'Multi-language Support', 'Hỗ trợ đa ngôn ngữ (Tiếng Việt, English) cho toàn bộ template và bot', 'FEATURE', 'IN DEVELOPMENT', 24],
    ['FW002', '2026-02-08T00:00:00Z', 'admin@freedomwallet.app', 'Export báo cáo tự động', 'Tự động gửi email báo cáo tài chính hàng tuần/tháng dạng PDF', 'FEATURE', 'IN DEVELOPMENT', 19],
    ['FW003', '2026-02-05T00:00:00Z', 'admin@freedomwallet.app', 'Tối ưu hiệu suất Dashboard', 'Cải thiện tốc độ load dashboard với lazy loading và caching thông minh', 'IMPROVEMENT', 'IN DEVELOPMENT', 11],
    
    // ============================================
    // TO DO - Approved and scheduled for development
    // ============================================
    ['FW011', '2026-02-01T00:00:00Z', 'admin@freedomwallet.app', 'Biểu đồ phân tích nâng cao', 'Thêm 5+ biểu đồ mới: Sankey, Heatmap, Treemap cho phân tích chi tiêu sâu hơn', 'FEATURE', 'TODO', 16],
    ['FW012', '2026-01-28T00:00:00Z', 'admin@freedomwallet.app', 'Recurring Transactions', 'Tự động tạo giao dịch định kỳ (lương, tiền nhà, học phí) hàng tháng', 'FEATURE', 'TODO', 21],
    ['FW013', '2026-01-25T00:00:00Z', 'admin@freedomwallet.app', 'Goal Tracking System', 'Thiết lập và theo dõi mục tiêu tài chính (mua nhà, du lịch, mua xe)', 'FEATURE', 'TODO', 14],
    
    // ============================================
    // BACKLOG - Community suggestions waiting for review
    // ============================================
    ['FW004', new Date().toISOString(), 'user@example.com', 'Kết nối ngân hàng tự động', 'Tự động sync giao dịch từ tài khoản ngân hàng qua API', 'FEATURE', 'BACKLOG', 15],
    ['FW005', new Date().toISOString(), 'user@example.com', 'Scan hóa đơn bằng AI', 'Chụp ảnh hóa đơn → AI OCR tự động thêm giao dịch', 'FEATURE', 'BACKLOG', 8],
    ['FW006', new Date().toISOString(), 'user@example.com', 'Mobile App iOS/Android', 'Ứng dụng mobile native cho iOS và Android', 'FEATURE', 'BACKLOG', 23],
    ['FW007', new Date().toISOString(), 'user@example.com', 'Dự báo chi tiêu AI', 'AI phân tích và dự đoán xu hướng chi tiêu, cảnh báo budget', 'FEATURE', 'BACKLOG', 12],
    ['FW008', new Date().toISOString(), 'user@example.com', 'Quản lý tài chính gia đình', 'Chia sẻ và quản lý ngân sách chung với nhiều thành viên', 'FEATURE', 'BACKLOG', 18],
    ['FW009', new Date().toISOString(), 'user@example.com', 'Export báo cáo PDF/Excel', 'Xuất báo cáo tài chính chi tiết dạng PDF/Excel', 'IMPROVEMENT', 'BACKLOG', 6],
    ['FW010', new Date().toISOString(), 'user@example.com', 'Dark mode cho webapp', 'Chế độ tối để bảo vệ mắt khi dùng ban đêm', 'IMPROVEMENT', 'BACKLOG', 9]
  ];
  
  sheet.getRange(2, 1, samples.length, samples[0].length).setValues(samples);
  Logger.log(`✅ Added ${samples.length} features (6 DONE + 3 IN DEVELOPMENT + 3 TODO + 7 BACKLOG)`);
}

// ============================================
// UPDATED HANDLERS (Thêm vào doGet/doPost hiện tại)
// ============================================

/**
 * THÊM VÀO FUNCTION doGet() HIỆN TẠI
 * Đặt code này TRƯỚC return statement cuối cùng trong doGet()
 */
function handleKanbanGetRequests(params) {
  // Get all features
  if (params.action === 'getFeatures') {
    try {
      const sheet = getOrCreateFeaturesSheet();
      const lastRow = sheet.getLastRow();
      
      if (lastRow <= 1) {
        return createJsonResponse(true, 'No features found', []);
      }
      
      const data = sheet.getRange(2, 1, lastRow - 1, 8).getValues();
      
      const features = data.map(row => ({
        id: row[0],
        timestamp: row[1],
        email: row[2],
        title: row[3],
        description: row[4],
        type: row[5],
        status: row[6],
        votes: row[7]
      }));
      
      return createJsonResponse(true, 'Features loaded', features);
      
    } catch (error) {
      logError('getFeatures', error);
      return createJsonResponse(false, 'Error loading features: ' + error.message);
    }
  }
}

/**
 * THÊM VÀO FUNCTION doPost() HIỆN TẠI
 * Đặt code này SAU parseRequestData() nhưng TRƯỚC validation
 */
function handleKanbanPostRequests(data) {
  // Add new feature
  if (data.action === 'addFeature') {
    try {
      const sheet = getOrCreateFeaturesSheet();
      
      // Generate unique ID
      const lastRow = sheet.getLastRow();
      const nextId = `FW${String(lastRow).padStart(3, '0')}`;
      
      // Validate input
      if (!data.email || !data.title || !data.description || !data.type) {
        return createJsonResponse(false, 'Missing required fields');
      }
      
      // Add to sheet
      const newRow = [
        nextId,
        data.timestamp || new Date().toISOString(),
        data.email,
        data.title,
        data.description,
        data.type,
        data.status || KANBAN_CONFIG.STATUSES.BACKLOG,  // User submissions go to BACKLOG first
        0  // Initial votes
      ];
      
      sheet.appendRow(newRow);
      
      logInfo('addFeature', `Added feature: ${data.title} by ${data.email}`);
      
      return createJsonResponse(true, 'Feature added successfully', {
        id: nextId,
        title: data.title
      });
      
    } catch (error) {
      logError('addFeature', error);
      return createJsonResponse(false, 'Error adding feature: ' + error.message);
    }
  }
  
  // Vote for feature
  if (data.action === 'voteFeature') {
    try {
      const featureSheet = getOrCreateFeaturesSheet();
      const voteSheet = getOrCreateVotesSheet();
      
      // Validate input
      if (!data.featureId || !data.email) {
        return createJsonResponse(false, 'Missing feature ID or email');
      }
      
      // Check if user already voted
      const voteData = voteSheet.getRange(2, 1, voteSheet.getLastRow() - 1, 3).getValues();
      const alreadyVoted = voteData.some(row => 
        row[1] === data.featureId && row[2] === data.email
      );
      
      if (alreadyVoted) {
        return createJsonResponse(false, 'You have already voted for this feature');
      }
      
      // Find feature and increment vote count
      const featureData = featureSheet.getRange(2, 1, featureSheet.getLastRow() - 1, 8).getValues();
      let featureRowIndex = -1;
      
      for (let i = 0; i < featureData.length; i++) {
        if (featureData[i][0] === data.featureId) {
          featureRowIndex = i + 2; // +2 because of header and 1-based indexing
          break;
        }
      }
      
      if (featureRowIndex === -1) {
        return createJsonResponse(false, 'Feature not found');
      }
      
      // Increment vote count
      const currentVotes = featureSheet.getRange(featureRowIndex, KANBAN_CONFIG.FEATURES_COLUMNS.VOTES + 1).getValue();
      featureSheet.getRange(featureRowIndex, KANBAN_CONFIG.FEATURES_COLUMNS.VOTES + 1).setValue(currentVotes + 1);
      
      // Record vote
      voteSheet.appendRow([
        data.timestamp || new Date().toISOString(),
        data.featureId,
        data.email
      ]);
      
      logInfo('voteFeature', `Vote recorded: ${data.email} voted for ${data.featureId}`);
      
      return createJsonResponse(true, 'Vote recorded successfully', {
        featureId: data.featureId,
        newVoteCount: currentVotes + 1
      });
      
    } catch (error) {
      logError('voteFeature', error);
      return createJsonResponse(false, 'Error recording vote: ' + error.message);
    }
  }
}

// ============================================
// HƯỚNG DẪN TÍCH HỢP
// ============================================

/**
 * BƯỚC 1: Sửa function doGet() hiện tại
 * 
 * Tìm dòng:
 *   const params = e.parameter || {};
 * 
 * Thêm NGAY SAU dòng đó:
 *   // Handle Kanban requests
 *   if (params.action === 'getFeatures') {
 *     return handleKanbanGetRequests(params);
 *   }
 */

/**
 * BƯỚC 2: Sửa function doPost() hiện tại
 * 
 * Tìm dòng:
 *   const data = parseRequestData(e);
 * 
 * Thêm NGAY SAU dòng đó:
 *   // Handle Kanban requests
 *   if (data.action === 'addFeature' || data.action === 'voteFeature') {
 *     return handleKanbanPostRequests(data);
 *   }
 */

/**
 * BƯỚC 3: Deploy lại Apps Script
 * 1. Click "Deploy" → "Manage deployments"
 * 2. Click icon ⚙️ bên cạnh "Active deployment"
 * 3. Chọn "New version"
 * 4. Click "Deploy"
 * 5. Copy URL mới (hoặc giữ URL cũ)
 */

/**
 * TEST FUNCTIONS (Chạy thủ công để test)
 */

function testCreateSheets() {
  getOrCreateFeaturesSheet();
  getOrCreateVotesSheet();
  Logger.log('✅ Sheets created successfully!');
}

function testGetFeatures() {
  const result = handleKanbanGetRequests({ action: 'getFeatures' });
  Logger.log(result.getContent());
}

function testAddFeature() {
  const result = handleKanbanPostRequests({
    action: 'addFeature',
    email: 'test@example.com',
    title: 'Test Feature',
    description: 'This is a test feature',
    type: 'FEATURE',
    status: 'TODO',
    timestamp: new Date().toISOString()
  });
  Logger.log(result.getContent());
}

function testVoteFeature() {
  const result = handleKanbanPostRequests({
    action: 'voteFeature',
    featureId: 'FW004',
    email: 'voter@example.com',
    timestamp: new Date().toISOString()
  });
  Logger.log(result.getContent());
}
