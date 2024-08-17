import os
from fastapi.responses import RedirectResponse, HTMLResponse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def get_flow():
    return InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)


def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                return RedirectResponse(url="/tilt/upload_credentials")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    SCOPES,
                    redirect_uri='https://localhost:8080/tilt/callback'
                )
                auth_url, _ = flow.authorization_url(prompt='consent')
                return RedirectResponse(url=auth_url)
    return creds

def list_shared_files(user_email):
    creds = authenticate()
    if isinstance(creds, RedirectResponse):
        return creds

    service = build('drive', 'v3', credentials=creds)

    query = "mimeType='application/vnd.google-apps.spreadsheet' and sharedWithMe"
    try:
        results = service.files().list(
            q=query,
            orderBy="modifiedTime desc",
            fields="nextPageToken, files(id, name, modifiedTime, owners)"
        ).execute()
    except HttpError as error:
        print(f"Error listing files: {error}")
        return []

    items = results.get('files', [])
    shared_sheets = []
    for item in items:
        try:
            owners = item.get('owners', [])
            shared_with_user = any(owner.get('emailAddress') == user_email for owner in owners)
            if shared_with_user:
                shared_sheets.append(item)
        except Exception as e:
            print(f"Error processing file ID {item['id']}: {e}")

    return shared_sheets


if __name__ == '__main__':
    files = list_shared_files(user_email)
    for file in files:
        print(f"{file['name']} ({file['id']}) - Modified on {file['modifiedTime']}")
