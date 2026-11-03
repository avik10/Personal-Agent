# Google Workspace MCP Server Guide

A Model Context Protocol (MCP) server connecting **Gmail**, **Google Drive**, **Google Calendar**, **Google Docs**, and **Google Tasks** to your AI assistants.

---

## 📋 Features & Registered Tools

The server registers **26 MCP tools** and an account status resource:

### ✉️ Gmail Tools
- `gmail_search_messages`: Search emails with full Gmail query syntax (`is:unread`, `from:boss`, `has:attachment`).
- `gmail_get_message`: Fetch email headers, snippets, and plain text content.
- `gmail_send_message`: Send emails with `to`, `subject`, `body`, and optional `cc`/`bcc`.
- `gmail_create_draft`: Compose email drafts directly in Gmail without sending.
- `gmail_list_labels`: List system folders (`INBOX`, `SENT`, `TRASH`) and custom labels.
- `gmail_modify_labels`: Mark read/unread, star, or archive messages.

### 📅 Google Calendar Tools
- `calendar_list_calendars`: List all Google Calendars in your account.
- `calendar_list_events`: Filter events by date range (`time_min`, `time_max`) and text search.
- `calendar_get_agenda`: Quick agenda helper for the next $N$ days (default 7 days).
- `calendar_create_event`: Create calendar events with description, attendees, and auto-generated Google Meet video links.
- `calendar_update_event`: Modify existing events (times, description, location).
- `calendar_delete_event`: Remove events from a calendar.

### 📁 Google Drive Tools
- `drive_search_files`: Search files and folders by name, type, or query.
- `drive_get_file_metadata`: Retrieve file metadata, web links, size, and permissions.
- `drive_read_file`: Read content of Drive files (automatically exports Google Docs to text and Sheets to CSV).
- `drive_upload_file`: Upload and create new text, markdown, or code files.
- `drive_create_folder`: Create a new directory/folder.
- `drive_delete_file`: Move files to trash or permanently delete.

### 📝 Google Docs Tools
- `docs_get_document`: Extract text and structural content from a Google Document.
- `docs_create_document`: Create a new Google Document with initial body text.
- `docs_append_text`: Append text or meeting summaries to the end of an existing doc.

### ✅ Google Tasks Tools
- `tasks_list_tasklists`: List your task lists.
- `tasks_list_tasks`: List active and completed tasks with due dates and notes.
- `tasks_create_task`: Create tasks with title, notes, and due dates.
- `tasks_complete_task`: Mark a task as completed.
- `tasks_delete_task`: Delete a task.

---

## 🔑 One-Time Setup: Google Cloud OAuth 2.0

### Step 1: Create a Google Cloud Project & Enable APIs
1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g. `Personal-AI-Assistant`).
3. In the search bar or under **APIs & Services > Library**, search for and **enable** each of these APIs:
   - **Gmail API**
   - **Google Calendar API**
   - **Google Drive API**
   - **Google Docs API**
   - **Google Tasks API**

### Step 2: Configure OAuth Consent Screen
1. Go to **APIs & Services > OAuth consent screen**.
2. Select **External** (or **Internal** if using Google Workspace organization) and click **Create**.
3. Fill in the required fields:
   - App name: `Personal MCP Assistant`
   - User support email: *Your email*
   - Developer contact email: *Your email*
4. Click **Save and Continue** through the Scopes page.
5. Under **Test Users**, click **+ ADD USERS** and add your Google email address.
6. Click **Save and Continue**.

### Step 3: Create Desktop Client ID
1. Go to **APIs & Services > Credentials**.
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**.
3. Application type: Select **Desktop app**.
4. Name: `Personal MCP Desktop`.
5. Click **Create**, then click **DOWNLOAD JSON** on the confirmation modal.
6. Save the downloaded file as:
   ```bash
   storage/google_credentials/credentials.json
   ```
   *(Or keep it at project root `credentials.json`)*.

---

## 🚀 Authenticate

Once you have placed `credentials.json`, run the setup utility:

```bash
python3 -m mcp_google setup
```

1. Your default web browser will open requesting consent.
2. Sign in with your Google account and grant the requested permissions.
3. Upon success, the terminal will verify all services and save `storage/google_credentials/token.json`.

To check your authentication status at any time:
```bash
python3 -m mcp_google check
```

---

## 🔌 Connecting to MCP Clients

### 1. Antigravity Configuration
In your Antigravity MCP settings (e.g. in your Antigravity configuration directory):

```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "python3",
      "args": [
        "-m",
        "mcp_google"
      ],
      "cwd": "/Users/avikbhattacharjya/Official/Development/AI/AI/Personal Agent"
    }
  }
}
```

### 2. Claude Desktop
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "python3",
      "args": [
        "-m",
        "mcp_google"
      ],
      "cwd": "/Users/avikbhattacharjya/Official/Development/AI/AI/Personal Agent"
    }
  }
}
```

### 3. Cursor
In Cursor Settings > Features > MCP:
- **Type**: `command`
- **Command**: `python3 -m mcp_google`
- **Working Directory**: `/Users/avikbhattacharjya/Official/Development/AI/AI/Personal Agent`

---

## 🔒 Security & Privacy

- **Local Storage**: Credentials and tokens are stored locally on your machine in `storage/google_credentials/`.
- **Git Excluded**: `.gitignore` is configured to prevent committing secrets or tokens.
- **Auto-Refresh**: Expired access tokens automatically refresh silently in the background using your refresh token without prompting you again.
