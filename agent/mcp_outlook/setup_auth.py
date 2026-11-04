"""CLI Helper to authenticate Microsoft Outlook via Microsoft Graph OAuth 2.0."""

import http.server
import socketserver
import urllib.parse
import webbrowser

from .auth import exchange_code_for_token, get_account_info, get_authorization_url
from .config import MICROSOFT_CLIENT_ID, TOKEN_PATH

PORT = 8089
REDIRECT_URI = f"http://localhost:{PORT}/callback"


class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    auth_code = None

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == "/callback":
            query = urllib.parse.parse_qs(url.query)
            if "code" in query:
                OAuthCallbackHandler.auth_code = query["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body style='font-family:sans-serif;text-align:center;padding:50px;'>"
                    b"<h2 style='color:#0078d4;'>&#10003; Microsoft Outlook Connected Successfully!</h2>"
                    b"<p>You can close this tab and return to the terminal or application.</p>"
                    b"</body></html>"
                )
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing code in callback.")
        else:
            self.send_response(404)
            self.end_headers()


def run_setup():
    print("=" * 65)
    print("  Microsoft Outlook MCP Server OAuth 2.0 Setup")
    print("=" * 65)

    if not MICROSOFT_CLIENT_ID:
        print("Error: MICROSOFT_CLIENT_ID is not configured in .env.")
        print("Please add MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET to .env.")
        return

    auth_url = get_authorization_url(redirect_uri=REDIRECT_URI)
    print(f"\nOpening browser for Microsoft Account login:\n{auth_url}\n")
    webbrowser.open(auth_url)

    print(f"Waiting for authentication on {REDIRECT_URI}...")
    with socketserver.TCPServer(("", PORT), OAuthCallbackHandler) as httpd:
        while not OAuthCallbackHandler.auth_code:
            httpd.handle_request()

    code = OAuthCallbackHandler.auth_code
    print("Authorization code received. Exchanging for tokens...")
    exchange_code_for_token(code=code, redirect_uri=REDIRECT_URI)

    print(f"Tokens saved to {TOKEN_PATH}!")
    try:
        info = get_account_info()
        print(f"Successfully authenticated as: {info.get('email')} ({info.get('displayName')})")
    except Exception as e:
        print(f"Warning: Could not fetch profile: {e}")


if __name__ == "__main__":
    run_setup()
