# 📝 Google Keep MCP Server Setup Guide

The **Google Keep MCP Server** connects your AI agents directly to your **real personal Google Keep account** (`https://keep.google.com`).

---

## Why a Dedicated Google Keep MCP Server?

Google restricts the raw Google Keep OAuth API to enterprise Google Workspace domain administrators, returning `Error 400: invalid_scope` on personal `@gmail.com` accounts.

This dedicated MCP server uses Google's standard App Password protocol to access your real Google Keep notes, checklists, colors, and pinned items with zero enterprise restrictions!

---

## Quick Setup (Takes 30 Seconds)

### Step 1: Generate a Google App Password
1. Visit: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   *(Ensure 2-Step Verification is enabled on your Google account).*
2. Under **App name**, type: `Personal Agent Keep`
3. Click **Create**.
4. Google will display a **16-character password** (e.g. `abcd efgh ijkl mnop`). Copy it.

### Step 2: Add to Your Environment
In your `.env` (or Render Dashboard ➔ Environment Variables):

```ini
GOOGLE_KEEP_EMAIL=your-email@gmail.com
GOOGLE_KEEP_APP_PASSWORD=abcdefghijklmnop
```

*(Note: The 16-character password can be entered with or without spaces).*

---

## Available MCP Tools

| MCP Tool Name | Description |
|---|---|
| `keep_list_notes` | List real notes from Google Keep (with optional search query, pinned filter) |
| `keep_get_note` | Get full details of a specific note by ID |
| `keep_create_note` | Create a new text note with title, body, color, and labels |
| `keep_create_checklist` | Create a to-do list / checklist note in Google Keep |
| `keep_update_note` | Update an existing note's title, text, or pin status |
| `keep_delete_note` | Move a note to trash or permanently delete it |
| `keep_search_notes` | Search Google Keep notes by keyword |

---

## Running the Google Keep MCP Server Standalone

You can run the MCP server standalone over standard input/output (stdio) for Claude Desktop, Cursor, or any MCP client:

```bash
python3 -m agent.mcp_google_keep
```
