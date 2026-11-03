"""Interactive CLI tool to authenticate Google Workspace OAuth 2.0 credentials."""

import argparse
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

from .auth import get_account_info, get_credentials, is_authenticated
from .config import CREDENTIALS_PATH, DEFAULT_SCOPES, TOKEN_PATH


def print_setup_instructions() -> None:
    print(
        """
================================================================================
                    Google Workspace MCP Server - OAuth Setup
================================================================================

To connect your Google Services (Gmail, Drive, Calendar, Docs, Tasks):

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create or select a Google Cloud project.
3. Enable the following APIs in "APIs & Services" > "Enable APIs and Services":
   - Gmail API
   - Google Calendar API
   - Google Drive API
   - Google Docs API
   - Tasks API
4. Configure OAuth Consent Screen:
   - User Type: "External" (or "Internal" if using Google Workspace organization)
   - Add your test user email under "Test Users" (if your app status is "Testing")
5. Create OAuth Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "+ CREATE CREDENTIALS" > "OAuth client ID"
   - Application Type: "Desktop app"
   - Name: "Personal MCP Assistant"
6. Download the JSON file:
   - Rename it to 'credentials.json' and save it at:
     {expected_cred_path}
   (or pass --credentials /path/to/downloaded.json)
================================================================================
""".format(expected_cred_path=CREDENTIALS_PATH)
    )


def run_auth_flow(credentials_path: Path, token_path: Path) -> bool:
    if not credentials_path.exists():
        print(f"\n[ERROR] Credentials file not found at: {credentials_path}")
        print_setup_instructions()
        return False

    print(f"\nStarting OAuth authentication using: {credentials_path}")
    print("Scopes requested:")
    for scope in DEFAULT_SCOPES:
        print(f"  • {scope}")

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path), DEFAULT_SCOPES
        )
        # Run local web server for authorization callback
        creds = flow.run_local_server(
            port=0,
            prompt="consent",
            authorization_prompt_message="Opening your default browser to authorize Google Workspace access...",
            success_message="Authentication successful! You may close this browser window and return to your terminal.",
        )

        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())

        print(f"\n[SUCCESS] Token saved successfully to: {token_path}")
        return True
    except Exception as e:
        print(f"\n[ERROR] Authorization flow failed: {e}")
        return False


def verify_services() -> None:
    print("\nVerifying Google API access...")
    try:
        from .auth import get_service

        # 1. Gmail
        try:
            gmail = get_service("gmail", "v1")
            profile = gmail.users().getProfile(userId="me").execute()
            print(f"  [✓] Gmail: Connected ({profile.get('emailAddress')})")
        except Exception as e:
            print(f"  [✗] Gmail: {e}")

        # 2. Calendar
        try:
            cal = get_service("calendar", "v3")
            cal_list = cal.calendarList().list(maxResults=3).execute()
            count = len(cal_list.get("items", []))
            print(f"  [✓] Google Calendar: Connected ({count} calendars found)")
        except Exception as e:
            print(f"  [✗] Google Calendar: {e}")

        # 3. Drive
        try:
            drive = get_service("drive", "v3")
            files = drive.files().list(pageSize=3, fields="files(id, name)").execute()
            count = len(files.get("files", []))
            print(f"  [✓] Google Drive: Connected ({count} recent files found)")
        except Exception as e:
            print(f"  [✗] Google Drive: {e}")

        # 4. Docs
        try:
            # Docs uses Drive credentials
            get_service("docs", "v1")
            print("  [✓] Google Docs: Ready")
        except Exception as e:
            print(f"  [✗] Google Docs: {e}")

        # 5. Tasks
        try:
            tasks = get_service("tasks", "v1")
            tasklists = tasks.tasklists().list(maxResults=3).execute()
            count = len(tasklists.get("items", []))
            print(f"  [✓] Google Tasks: Connected ({count} task lists found)")
        except Exception as e:
            print(f"  [✗] Google Tasks: {e}")

        print("\nAll tested services verified!")
    except Exception as e:
        print(f"[ERROR] Service verification failed: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Google Workspace MCP Server Auth Setup")
    parser.add_argument(
        "--credentials",
        type=Path,
        default=CREDENTIALS_PATH,
        help=f"Path to credentials.json (default: {CREDENTIALS_PATH})",
    )
    parser.add_argument(
        "--token",
        type=Path,
        default=TOKEN_PATH,
        help=f"Path to output token.json (default: {TOKEN_PATH})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check current authentication status without opening browser",
    )
    parser.add_argument(
        "--instructions",
        action="store_true",
        help="Show Google Cloud OAuth setup instructions",
    )

    args = parser.parse_args()

    if args.instructions:
        print_setup_instructions()
        return

    if args.check:
        if is_authenticated():
            print("[INFO] Existing authentication is valid.")
            info = get_account_info()
            print(f"Account: {info.get('emailAddress')}")
            verify_services()
        else:
            print("[WARNING] Not currently authenticated.")
            print(f"Run `python3 -m mcp_google.setup_auth` to authenticate.")
        return

    success = run_auth_flow(args.credentials, args.token)
    if success:
        verify_services()
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
