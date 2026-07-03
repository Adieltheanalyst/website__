/**
 * BuildIT Connective — Google Form → Website Sync
 * ═══════════════════════════════════════════════
 *
 * SETUP (one time, takes 5 minutes):
 *
 * 1. Open your Google Sheet (the one linked to your Google Form)
 * 2. Click Extensions → Apps Script
 * 3. Delete everything and paste this entire file
 * 4. Update the 3 config values below (YOUR_WEBSITE_URL, YOUR_SECRET, COLUMN NUMBERS)
 * 5. Click Save (floppy disk icon)
 * 6. Click the dropdown next to "Run" → select "onFormSubmit"
 * 7. Click Run once to grant permissions (you'll see a Google warning — click "Advanced" → "Go to BuildIT")
 * 8. Click Triggers (clock icon on left sidebar)
 * 9. Click "+ Add Trigger" → choose:
 *      Function: onFormSubmit
 *      Event source: From spreadsheet
 *      Event type: On form submit
 * 10. Save
 *
 * That's it! Now every form submission auto-appears in your /admin panel as pending.
 */

// ─── CONFIG — update these 3 things ───────────────────────────────
var WEBSITE_URL = "https://YOUR-SITE.com/api/form-submission";
// ^ Replace with your actual deployed URL, e.g. https://builditconnective.up.railway.app/api/form-submission
// ^ For local testing use ngrok (see README)

var WEBHOOK_SECRET = "buildit-sheets-secret-change-me";
// ^ Must exactly match SHEETS_WEBHOOK_SECRET in your app.py / environment

// Column numbers in your Google Sheet (1 = column A, 2 = column B, etc.)
// Open your Sheet and count which column has each field
var COLUMNS = {
  timestamp: 1,   // Column A — always added by Google Forms automatically
  name:      2,   // Column B — "Full name" question
  email:     3,   // Column C — "Email address" question
  phone:     4,   // Column D — "Phone number" question (or 0 if you don't have it)
  about:     5,   // Column E — "Tell us about yourself" question (or 0 if you don't have it)
};
// ──────────────────────────────────────────────────────────────────


function onFormSubmit(e) {
  try {
    var row = e.values; // Array of cell values from the submitted row

    // Pull values using column config (subtract 1 because arrays are 0-indexed)
    var name  = COLUMNS.name  > 0 ? (row[COLUMNS.name  - 1] || "").trim() : "";
    var email = COLUMNS.email > 0 ? (row[COLUMNS.email - 1] || "").trim() : "";
    var phone = COLUMNS.phone > 0 ? (row[COLUMNS.phone - 1] || "").trim() : "";
    var about = COLUMNS.about > 0 ? (row[COLUMNS.about - 1] || "").trim() : "";

    if (!name || !email) {
      Logger.log("Skipping row — missing name or email");
      return;
    }

    // Build the payload to send to Flask
    var payload = {
      secret: WEBHOOK_SECRET,
      name:   name,
      email:  email,
      phone:  phone,
      about:  about,
    };

    // Send to your Flask API
    var options = {
      method:      "post",
      contentType: "application/json",
      payload:     JSON.stringify(payload),
      muteHttpExceptions: true, // Don't crash if server returns an error
    };

    var response = UrlFetchApp.fetch(WEBSITE_URL, options);
    var code     = response.getResponseCode();
    var body     = response.getContentText();

    Logger.log("Response " + code + ": " + body);

    // Optional: add a note in the sheet so you can see it was synced
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var lastCol = sheet.getLastColumn();
    var lastRow = e.range.getRow();
    sheet.getRange(lastRow, lastCol + 1).setValue(
      code === 200 || code === 201 ? "✅ Synced to site" : "⚠️ Sync failed (" + code + ")"
    );

  } catch (err) {
    Logger.log("Error in onFormSubmit: " + err.toString());
  }
}


/**
 * TEST FUNCTION — run this manually to check the connection works
 * before waiting for a real form submission.
 * Click the function dropdown → select "testWebhook" → click Run
 */
function testWebhook() {
  var payload = {
    secret: WEBHOOK_SECRET,
    name:   "Test Member",
    email:  "test@builditconnective.com",
    phone:  "+254 700 000000",
    about:  "This is a test submission from Apps Script",
  };

  var options = {
    method:      "post",
    contentType: "application/json",
    payload:     JSON.stringify(payload),
    muteHttpExceptions: true,
  };

  var response = UrlFetchApp.fetch(WEBSITE_URL, options);
  Logger.log("Test response " + response.getResponseCode() + ": " + response.getContentText());
  // Open View → Logs to see the result
}
