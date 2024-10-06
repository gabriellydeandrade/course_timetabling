# https://developers.google.com/sheets/api/quickstart/python

import os.path
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

SAMPLE_SPREADSHEET_ID = "1MZ_LFco9SZ5FrZFt7CAUCJu4xHov9VtTuil0CyRx9jI"



def read_google_sheet_to_dataframe(spreadsheet_id, range_name):
    """Reads data from a Google Sheet and returns it as a pandas DataFrame."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return pd.DataFrame()

        # Convert the values to a pandas DataFrame
        df = pd.DataFrame(values[1:], columns=values[0])
        return df

    except HttpError as err:
        print(err)
        return pd.DataFrame()


def get_courses(page_name: str):
    pass


def get_professors():
    page_name = "professores!A:K"
    df = read_google_sheet_to_dataframe(SAMPLE_SPREADSHEET_ID, page_name)

    professors_availables = df.loc[df["Alocar"] == "TRUE"].filter(["Nome curto", "Disciplinas aptas", "Área de conhecimento", "Categoria"])
    professors_availables.rename(columns={"Nome curto": "professor", "Disciplinas aptas": "qualified_courses", "Área de conhecimento": "expertise", "Categoria": "category"}, inplace=True)
    professors_availables.set_index("professor", inplace=True)
    
    permanent = professors_availables.loc[(~professors_availables["category"].isin(["PS", "EX", "AP"]))]
    substitute = professors_availables.loc[(professors_availables["category"] == "PS")]

    return permanent, substitute



