/**
 * BuildIT Connective — Google Form → Flask Sync
 * ═══════════════════════════════════════════════
 * HOW TO SET THIS UP (takes ~5 minutes):
 *
 * 1. Open your Google Sheet (the one linked to your Google Form)
 * 2. Click Extensions → Apps Script
 * 3. Delete everything in the editor
 * 4. Paste this entire file
 * 5. Update the two CONFIG values below
 * 6. Click Save (floppy disk icon)
 * 7. Click "Add Trigger" (clock icon on left sidebar):
 *      - Function: onFormSubmit
 *      - Event source: From spreadsheet
 *      - Event type: On form submit
 *      - Click Save → approve Google permissions
 * 8. Done! Test by submitting the form once.
 *
 * To check logs: Extensions → Apps Script → Executions (left sidebar)
 */

// ─── CONFIG — update these two values ───────────────────────────────────────

var FLASK_URL = "https://YOUR-SITE.com/api/new-member";
// ↑ Replace with your actual URL when deployed.
//   For local testing use ngrok: https://abc123.ngrok.io/api/new-member

var WEBHOOK_SECRET = "buildit-sheets-sync-2025";
// ↑ Must match WEBHOOK_SECRET in your app.py exactly

// ────────────────────────────────────────────────────────────────────────────


/**
 * Runs automatically every time someone submits the Google Form.
 * Maps form columns to the fields Flask expects.
 *
 * IMPORTANT: Check your column names match below.
 * Open your Sheet, look at row 1 (headers), update the mapping if needed.
 */

function onFormSubmit(e) {

  // ── Get the submitted row ─────────────────────────────────────────────────
  var row    = e.values;         // array of cell values in order
  var headers = getHeaders();    // column names from row 1

  // Build a key→value map so we can look up by column name
  var data = {};
  for (var i = 0; i < headers.length; i++) {
    data[headers[i]] = row[i] || "";
  }

  Logger.log("Form submission received: " + JSON.stringify(data));

  // ── Map your form fields → Flask fields ──────────────────────────────────
  // Look at your Google Form column headers and update these strings to match.
  // Common names are shown as comments.

var payload = {
  secret:    WEBHOOK_SECRET,
  name:      findField(data, FIELD_MAP.name),
  email:     findField(data, FIELD_MAP.email),
  phone:     findField(data, FIELD_MAP.phone),
  role:      findField(data, FIELD_MAP.role),
  location:  findField(data, FIELD_MAP.location),
  age_range: findField(data, FIELD_MAP.age_range),
  community: findField(data, FIELD_MAP.community),
  education: findField(data, FIELD_MAP.education),
};
  Logger.log("Sending to Flask: " + JSON.stringify(payload));

  // ── Send to Flask ─────────────────────────────────────────────────────────
  try {
    var options = {
      method:      "post",
      contentType: "application/json",
      payload:     JSON.stringify(payload),
      muteHttpExceptions: true,   // don't throw on 4xx/5xx, just log
    };

    var response = UrlFetchApp.fetch(FLASK_URL, options);
    var code     = response.getResponseCode();
    var body     = response.getContentText();

    Logger.log("Flask response (" + code + "): " + body);

    // ── Write status back into the Sheet ──────────────────────────────────
    // Adds a "Sync Status" column so you can see what happened per row
    var sheet      = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var lastRow    = sheet.getLastRow();
    var lastCol    = sheet.getLastColumn();

    // Find or create "Sync Status" column
    var statusCol = findOrCreateColumn(sheet, "Sync Status");
    var syncCell  = sheet.getRange(lastRow, statusCol);

    if (code === 200 || code === 201) {
      var result = JSON.parse(body);
      if (result.status === "already_exists") {
        syncCell.setValue("⚠️ Already in DB (" + result.member_status + ")");
        syncCell.setBackground("#fff3cd");
      } else {
        syncCell.setValue("✅ Synced — pending approval");
        syncCell.setBackground("#d4edda");
      }
    } else {
      syncCell.setValue("❌ Error " + code + ": " + body);
      syncCell.setBackground("#f8d7da");
    }

  } catch (err) {
    Logger.log("Error sending to Flask: " + err.toString());

    // Mark the row as failed in the sheet
    var sheet   = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var lastRow = sheet.getLastRow();
    var statusCol = findOrCreateColumn(sheet, "Sync Status");
    sheet.getRange(lastRow, statusCol).setValue("❌ Script error: " + err.toString());
  }
}


/**
 * Test function — run this manually from Apps Script to check the connection
 * without needing to submit a real form.
 * Click the function name, then click Run (▶).
 */
function testConnection() {
  var payload = {
    secret: WEBHOOK_SECRET,
    name:   "Test Member",
    email:  "test@builditconnective.com",
    phone:  "+254700000000",
    role:   "Developer",
  };

  var options = {
    method:      "post",
    contentType: "application/json",
    payload:     JSON.stringify(payload),
    muteHttpExceptions: true,
  };

  Logger.log("Testing connection to: " + FLASK_URL);

  try {
    var response = UrlFetchApp.fetch(FLASK_URL, options);
    Logger.log("Status: " + response.getResponseCode());
    Logger.log("Body:   " + response.getContentText());
    SpreadsheetApp.getUi().alert(
      "✅ Connection successful!\n\n" + response.getContentText()
    );
  } catch (err) {
    Logger.log("Failed: " + err.toString());
    SpreadsheetApp.getUi().alert(
      "❌ Connection failed:\n\n" + err.toString() +
      "\n\nMake sure your Flask server is running and the URL is correct."
    );
  }
}


/**
 * Sync all existing rows from the sheet (run once to backfill)
 * Useful if you already have people in the sheet before setting this up.
 */
function syncAllExisting() {
  var sheet   = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var headers = getHeaders();
  var data    = sheet.getDataRange().getValues();
  var synced = 0, skipped = 0, errors = 0;

  // Start from row 2 (skip headers)
  for (var i = 1; i < data.length; i++) {
    var row = {};
    for (var j = 0; j < headers.length; j++) {
      row[headers[j]] = data[i][j] || "";
    }

    var payload = {
      secret: WEBHOOK_SECRET,
      name:   findField(row, ["Full Name", "Name", "Your Name", "Full name"]),
      email:  findField(row, ["Email", "Email Address", "Email address", "E-mail"]),
      phone:  findField(row, ["Phone", "Phone Number", "WhatsApp", "Mobile"]),
      role:   findField(row, ["Role", "Your Role", "What do you do", "Skill", "Background"]),
    };

    if (!payload.email) { skipped++; continue; }

    try {
      var response = UrlFetchApp.fetch(FLASK_URL, {
        method: "post",
        contentType: "application/json",
        payload: JSON.stringify(payload),
        muteHttpExceptions: true,
      });
      if (response.getResponseCode() < 300) synced++;
      else errors++;
    } catch(e) {
      errors++;
    }

    Utilities.sleep(300); // be gentle, don't hammer the server
  }

  SpreadsheetApp.getUi().alert(
    "Sync complete!\n\n" +
    "✅ Synced: " + synced + "\n" +
    "⚠️ Skipped (no email): " + skipped + "\n" +
    "❌ Errors: " + errors
  );
}


// ─── Helpers ─────────────────────────────────────────────────────────────────

function getHeaders() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  return sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
}

// Try multiple possible column names (form labels vary)
function findField(data, possibleKeys) {
  for (var i = 0; i < possibleKeys.length; i++) {
    if (data[possibleKeys[i]] !== undefined && data[possibleKeys[i]] !== "") {
      return data[possibleKeys[i]];
    }
  }
  return "";
}

function findOrCreateColumn(sheet, colName) {
  var headers  = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var colIndex = headers.indexOf(colName);
  if (colIndex >= 0) return colIndex + 1;
  // Create new column at the end
  var newCol = sheet.getLastColumn() + 1;
  sheet.getRange(1, newCol).setValue(colName);
  return newCol;
}
