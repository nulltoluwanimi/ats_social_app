from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

scopes = ['https://www.googleapis.com/auth/calendar']

flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=scopes)

flow.run_console()