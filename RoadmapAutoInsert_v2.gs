/**
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * FREEDOM WALLET - DYNAMIC ROADMAP AUTOMATION v2.0
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * 
 * Replaces static insertRoadmapV330() with dynamic governance system
 * 
 * Features:
 * - insertRoadmapItem(data) - Add new roadmap item
 * - updateRoadmapStatus(id, newStatus) - Update status by ID
 * - updateRoadmapByTitle(title, newStatus) - Update status by Title
 * - logReleaseVersion(version, description) - Log release
 * - Auto-duplicate removal
 * - Conditional formatting
 * 
 * Author: Freedom Wallet Team
 * Version: 2.0
 * Date: 2026-02-17
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

// ⚠️ Đổi tên CONFIG → ROADMAP_CONFIG để tránh conflict với Code.gs
const ROADMAP_CONFIG = {
  // 🔧 IMPORTANT: Đổi tên sheet phù hợp với Google Sheet của bạn
  // Ví dụ: 'Sheet1', 'Roadmap', 'Features', etc.
  SHEET_NAME: 'Roadmap_Features',  // ⚠️ KIỂM TRA TÊN SHEET!
  
  
  COLUMNS: {
    ID: 1,
    TIMESTAMP: 2,
    EMAIL: 3,
    TITLE: 4,
    DESCRIPTION: 5,
    TYPE: 6,
    STATUS: 7,
    VOTES: 8
  },
  DEFAULT_EMAIL: 'system@freedomwallet.com',
  STATUSES: {
    IDEA: 'IDEA',
    PLANNED: 'PLANNED',
    IN_PROGRESS: 'IN_PROGRESS',
    COMPLETED: 'COMPLETED',
    REFACTORED: 'REFACTORED',
    RELEASED: 'RELEASED',
    ARCHITECTURE_UPDATE: 'ARCHITECTURE_UPDATE'
  },
  TYPES: {
    FEATURE: 'Tính năng',
    BUG_FIX: 'Bug Fix',
    UI_UX: 'UI/UX',
    RELEASE: 'Release',
    ARCHITECTURE: 'Architecture',
    REFACTOR: 'Refactor'
  }
};

// ============================================================================
// CORE FUNCTIONS - Dynamic Roadmap Management
// ============================================================================

/**
 * Insert new roadmap item dynamically
 * 
 * @param {Object} data - Roadmap item data
 * @param {string} data.id - Unique ID (e.g., "FW#123")
 * @param {string} data.title - Item title
 * @param {string} data.description - Item description
 * @param {string} data.type - Type (FEATURE, BUG_FIX, etc.)
 * @param {string} data.status - Status (IDEA, PLANNED, etc.)
 * @param {string} [data.email] - Reporter email (optional)
 * @param {number} [data.votes] - Initial votes (optional, default=0)
 * 
 * @return {Object} Result object with success status and message
 * 
 * @example
 * insertRoadmapItem({
 *   id: "FW#150",
 *   title: "AI Budget Recommendations",
 *   description: "Auto-suggest budget allocation based on spending patterns",
 *   type: ROADMAP_CONFIG.TYPES.FEATURE,
 *   status: ROADMAP_CONFIG.STATUSES.IDEA,
 *   email: "user@example.com"
 * });
 */
function insertRoadmapItem(data) {
  try {
    const sheet = getSheet();
    
    // Validation
    if (!data || !data.title) {
      return { success: false, message: 'Missing required field: title' };
    }
    
    // Check for duplicates
    const existingTitles = getExistingTitles(sheet);
    if (existingTitles.has(data.title.trim())) {
      Logger.log(`⚠️ Duplicate title: ${data.title}`);
      return { success: false, message: `Item already exists: ${data.title}` };
    }
    
    // Auto-generate ID if not provided
    const itemId = data.id || generateNextId(sheet);
    
    // Prepare row data
    const newRow = [
      itemId,
      new Date(),
      data.email || ROADMAP_CONFIG.DEFAULT_EMAIL,
      data.title,
      data.description || '',
      data.type || ROADMAP_CONFIG.TYPES.FEATURE,
      data.status || ROADMAP_CONFIG.STATUSES.IDEA,
      data.votes || 0
    ];
    
    // Insert row
    const lastRow = sheet.getLastRow();
    sheet.getRange(lastRow + 1, 1, 1, 8).setValues([newRow]);
    
    // Apply formatting
    applyStatusFormatting(sheet, lastRow + 1, 1);
    
    Logger.log(`✅ Inserted: ${itemId} - ${data.title}`);
    return { 
      success: true, 
      message: `Added: ${itemId} - ${data.title}`,
      id: itemId,
      row: lastRow + 1
    };
    
  } catch (error) {
    Logger.log(`❌ Error in insertRoadmapItem: ${error}`);
    return { success: false, message: error.toString() };
  }
}


/**
 * Update roadmap item status by ID
 * 
 * @param {string} id - Item ID (e.g., "FW#123")
 * @param {string} newStatus - New status value
 * @param {string} [notes] - Optional notes for the update
 * 
 * @return {Object} Result object
 * 
 * @example
 * updateRoadmapStatus("FW#123", CONFIG.STATUSES.IN_PROGRESS);
 */
function updateRoadmapStatus(id, newStatus, notes) {
  try {
    const sheet = getSheet();
    const data = sheet.getDataRange().getValues();
    
    // Find row with matching ID
    for (let i = 1; i < data.length; i++) {
      if (data[i][0] === id) {
        const row = i + 1;
        
        // Update status
        sheet.getRange(row, ROADMAP_CONFIG.COLUMNS.STATUS).setValue(newStatus);
        
        // Update timestamp
        sheet.getRange(row, ROADMAP_CONFIG.COLUMNS.TIMESTAMP).setValue(new Date());
        
        // Add notes to description if provided
        if (notes) {
          const currentDesc = data[i][4];
          const newDesc = `${currentDesc}\n\n[${newStatus}] ${notes}`;
          sheet.getRange(row, ROADMAP_CONFIG.COLUMNS.DESCRIPTION).setValue(newDesc);
        }
        
        // Apply formatting
        applyStatusFormatting(sheet, row, 1);
        
        Logger.log(`✅ Updated ${id}: ${newStatus}`);
        return { 
          success: true, 
          message: `Updated ${id} → ${newStatus}`,
          row: row
        };
      }
    }
    
    return { success: false, message: `ID not found: ${id}` };
    
  } catch (error) {
    Logger.log(`❌ Error in updateRoadmapStatus: ${error}`);
    return { success: false, message: error.toString() };
  }
}


/**
 * Update roadmap item status by Title
 * 
 * @param {string} title - Item title (exact match)
 * @param {string} newStatus - New status value
 * 
 * @return {Object} Result object
 * 
 * @example
 * updateRoadmapByTitle("AI Budget Recommendations", ROADMAP_CONFIG.STATUSES.COMPLETED);
 */
function updateRoadmapByTitle(title, newStatus) {
  try {
    const sheet = getSheet();
    const data = sheet.getDataRange().getValues();
    
    // Find row with matching title
    for (let i = 1; i < data.length; i++) {
      if (data[i][3].trim() === title.trim()) {
        const itemId = data[i][0];
        return updateRoadmapStatus(itemId, newStatus);
      }
    }
    
    return { success: false, message: `Title not found: ${title}` };
    
  } catch (error) {
    Logger.log(`❌ Error in updateRoadmapByTitle: ${error}`);
    return { success: false, message: error.toString() };
  }
}


/**
 * Log a new release version
 * 
 * @param {string} version - Version number (e.g., "v2.0.0")
 * @param {string} description - Release description
 * @param {Array<string>} features - List of features included
 * 
 * @return {Object} Result object
 * 
 * @example
 * logReleaseVersion("v2.0.0", "Unified Flow Architecture", [
 *   "State machine refactor",
 *   "Dynamic roadmap system",
 *   "CHANGELOG integration"
 * ]);
 */
function logReleaseVersion(version, description, features) {
  try {
    const featureList = features && features.length > 0 
      ? '\n\nFeatures:\n- ' + features.join('\n- ')
      : '';
    
    const releaseData = {
      id: `RELEASE-${version}`,
      title: `Release ${version}`,
      description: description + featureList,
      type: ROADMAP_CONFIG.TYPES.RELEASE,
      status: ROADMAP_CONFIG.STATUSES.RELEASED,
      email: 'release@freedomwallet.com',
      votes: 0
    };
    
    const result = insertRoadmapItem(releaseData);
    
    if (result.success) {
      // Also update all COMPLETED items to RELEASED
      batchUpdateStatus(ROADMAP_CONFIG.STATUSES.COMPLETED, ROADMAP_CONFIG.STATUSES.RELEASED);
    }
    
    return result;
    
  } catch (error) {
    Logger.log(`❌ Error in logReleaseVersion: ${error}`);
    return { success: false, message: error.toString() };
  }
}


/**
 * Batch update status for multiple items
 * 
 * @param {string} oldStatus - Current status to match
 * @param {string} newStatus - New status to set
 * 
 * @return {Object} Result with count of updated items
 */
function batchUpdateStatus(oldStatus, newStatus) {
  try {
    const sheet = getSheet();
    const data = sheet.getDataRange().getValues();
    let count = 0;
    
    for (let i = 1; i < data.length; i++) {
      if (data[i][6] === oldStatus) {
        sheet.getRange(i + 1, ROADMAP_CONFIG.COLUMNS.STATUS).setValue(newStatus);
        applyStatusFormatting(sheet, i + 1, 1);
        count++;
      }
    }
    
    Logger.log(`✅ Batch update: ${count} items ${oldStatus} → ${newStatus}`);
    return { success: true, message: `Updated ${count} items`, count: count };
    
  } catch (error) {
    Logger.log(`❌ Error in batchUpdateStatus: ${error}`);
    return { success: false, message: error.toString() };
  }
}


// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get sheet reference
 */
function getSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(ROADMAP_CONFIG.SHEET_NAME);
  
  if (!sheet) {
    throw new Error(`Sheet not found: ${ROADMAP_CONFIG.SHEET_NAME}`);
  }
  
  return sheet;
}


/**
 * Get all existing titles for duplicate checking
 */
function getExistingTitles(sheet) {
  const lastRow = sheet.getLastRow();
  
  if (lastRow <= 1) {
    return new Set();
  }
  
  const titleColumn = sheet.getRange(2, ROADMAP_CONFIG.COLUMNS.TITLE, lastRow - 1, 1).getValues();
  const titles = new Set();
  
  titleColumn.forEach(row => {
    if (row[0]) {
      titles.add(row[0].toString().trim());
    }
  });
  
  return titles;
}


/**
 * Generate next ID (auto-increment)
 */
function generateNextId(sheet) {
  const data = sheet.getDataRange().getValues();
  let maxId = 0;
  
  for (let i = 1; i < data.length; i++) {
    const id = data[i][0];
    if (id && id.startsWith('FW#')) {
      const num = parseInt(id.replace('FW#', ''));
      if (!isNaN(num) && num > maxId) {
        maxId = num;
      }
    }
  }
  
  return `FW#${String(maxId + 1).padStart(3, '0')}`;
}


/**
 * Apply conditional formatting to status column
 */
function applyStatusFormatting(sheet, startRow, numRows) {
  const statusRange = sheet.getRange(startRow, ROADMAP_CONFIG.COLUMNS.STATUS, numRows, 1);
  const statusValues = statusRange.getValues();
  const backgrounds = [];
  const fontColors = [];
  
  statusValues.forEach(row => {
    const status = row[0];
    let bgColor, fgColor;
    
    switch(status) {
      case ROADMAP_CONFIG.STATUSES.RELEASED:
        bgColor = '#b7e1cd'; // Light green
        fgColor = '#0d652d'; // Dark green
        break;
      case ROADMAP_CONFIG.STATUSES.COMPLETED:
        bgColor = '#d4edda'; // Green
        fgColor = '#155724';
        break;
      case ROADMAP_CONFIG.STATUSES.REFACTORED:
        bgColor = '#cfe2ff'; // Light blue
        fgColor = '#084298';
        break;
      case ROADMAP_CONFIG.STATUSES.IN_PROGRESS:
        bgColor = '#fff3cd'; // Orange
        fgColor = '#856404';
        break;
      case ROADMAP_CONFIG.STATUSES.PLANNED:
        bgColor = '#d1ecf1'; // Blue
        fgColor = '#0c5460';
        break;
      case ROADMAP_CONFIG.STATUSES.IDEA:
        bgColor = '#f8d7da'; // Light pink
        fgColor = '#721c24';
        break;
      case ROADMAP_CONFIG.STATUSES.ARCHITECTURE_UPDATE:
        bgColor = '#e7e8ea'; // Gray
        fgColor = '#1c1e21';
        break;
      default:
        bgColor = '#ffffff';
        fgColor = '#000000';
    }
    
    backgrounds.push([bgColor]);
    fontColors.push([fgColor]);
  });
  
  statusRange.setBackgrounds(backgrounds);
  statusRange.setFontColors(fontColors);
  statusRange.setFontWeight('bold');
}


/**
 * Remove duplicate rows by Title (cleanup utility)
 */
function removeDuplicatesByTitle(sheet) {
  const lastRow = sheet.getLastRow();
  
  if (lastRow <= 1) {
    return 0;
  }
  
  const dataRange = sheet.getRange(2, 1, lastRow - 1, 8);
  const data = dataRange.getValues();
  
  const seenTitles = new Set();
  const rowsToDelete = [];
  
  for (let i = 0; i < data.length; i++) {
    const title = data[i][3];
    
    if (!title) continue;
    
    const titleNormalized = title.toString().trim();
    
    if (seenTitles.has(titleNormalized)) {
      rowsToDelete.push(i + 2);
    } else {
      seenTitles.add(titleNormalized);
    }
  }
  
  rowsToDelete.reverse().forEach(rowNumber => {
    sheet.deleteRow(rowNumber);
  });
  
  return rowsToDelete.length;
}


// ============================================================================
// MANUAL EXECUTION FUNCTIONS (For testing)
// ============================================================================

/**
 * Test: Insert a sample roadmap item
 */
function testInsertItem() {
  const result = insertRoadmapItem({
    title: "Test: Dynamic Roadmap System",
    description: "Testing the new dynamic roadmap automation v2.0",
    type: ROADMAP_CONFIG.TYPES.FEATURE,
    status: ROADMAP_CONFIG.STATUSES.IN_PROGRESS,
    email: "test@freedomwallet.com"
  });
  
  Logger.log(result);
  SpreadsheetApp.getUi().alert(result.message);
}


/**
 * Test: Update item status
 */
function testUpdateStatus() {
  const result = updateRoadmapByTitle(
    "Test: Dynamic Roadmap System", 
    ROADMAP_CONFIG.STATUSES.COMPLETED
  );
  
  Logger.log(result);
  SpreadsheetApp.getUi().alert(result.message);
}


/**
 * Test: Log a release
 */
function testLogRelease() {
  const result = logReleaseVersion(
    "v2.0.0",
    "Unified Flow Architecture Release",
    [
      "State machine refactor",
      "Dynamic roadmap system",
      "CHANGELOG integration",
      "Automated testing suite"
    ]
  );
  
  Logger.log(result);
  SpreadsheetApp.getUi().alert(result.message);
}


/**
 * Cleanup: Remove duplicates
 */
function cleanupDuplicates() {
  const sheet = getSheet();
  const removed = removeDuplicatesByTitle(sheet);
  
  SpreadsheetApp.getUi().alert(
    `🧹 Cleanup complete!\n\nRemoved ${removed} duplicate rows`
  );
}


// ============================================================================
// MIGRATION: Import from old static function
// ============================================================================

/**
 * Migrate data from old insertRoadmapV330() format
 * Run this once to migrate existing hardcoded data
 */
function migrateOldData() {
  // Example migration - adapt to your old data structure
  const oldData = [
    // Your old hardcoded array here
  ];
  
  let successCount = 0;
  let errorCount = 0;
  
  oldData.forEach(row => {
    const result = insertRoadmapItem({
      id: row[0],
      title: row[3],
      description: row[4],
      type: row[5],
      status: row[6],
      email: row[2],
      votes: row[7]
    });
    
    if (result.success) {
      successCount++;
    } else {
      errorCount++;
    }
  });
  
  Logger.log(`Migration: ${successCount} success, ${errorCount} errors`);
}
