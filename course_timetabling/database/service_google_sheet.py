# https://developers.google.com/sheets/api/quickstart/python

import os.path
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from cache_pandas import cache_to_csv

import settings


def read_google_sheet_to_dataframe(spreadsheet_id, range_name):
    """
    Reads data from a Google Sheet and returns it as a pandas DataFrame.

    Args:
        spreadsheet_id (str): The ID of the Google Spreadsheet.
        range_name (str): The range of cells to read from the spreadsheet.

    Returns:
        pd.DataFrame: A DataFrame containing the data read from the Google Sheet.

    Note:
        It is not necessary to test this function, as it is a wrapper for the Google Sheets API and used with the Google website example.
    """
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json", settings.APP_SHEETS_SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", settings.APP_SHEETS_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        sheet = service.spreadsheets()
        result = (
            sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return pd.DataFrame()

        df = pd.DataFrame(values[1:], columns=values[0])
        return df

    except HttpError as err:
        print(err)
        return pd.DataFrame()


@cache_to_csv("cache/get_required_courses.csv", refresh_time=settings.APP_CACHE_TTL)
def get_required_courses() -> pd.DataFrame:
    """
    Retrieves required courses from a Google Sheet and returns them as a pandas DataFrame.
    This function reads data from the "disciplinas_obrigatorias" sheet in the specified Google Sheet.
    It filters the courses that need to be allocated (where "Alocar" is "TRUE") and selects specific columns.
    The resulting DataFrame is then renamed and indexed by the unique course class ID.
    Returns:
        pd.DataFrame: A DataFrame containing the required courses with the following columns:
            - course_class_id: Unique class ID
            - course_id: Course ID
            - course_name: Course name
            - graduation_course: Graduation course
            - credits: Number of credits
            - day: Day of the week
            - time: Time
            - course_type: Type of course
            - capacity: Number of students
            - class_type: Type of class
            - responsable_institute: Responsible institute
            - classroom_type: Type of classroom
            - term: Term
    """

    page_name = "disciplinas_obrigatorias!A:S"
    df = read_google_sheet_to_dataframe(settings.SAMPLE_SPREADSHEET_ID, page_name)

    courses = df.loc[df["Alocar"] == "TRUE"].filter(
        [
            "Código único turma",
            "Código disciplina",
            "Nome disciplina",
            "Curso",
            "Qtd de créditos",
            "Dia da semana",
            "Horário",
            "Tipo disciplina",
            "Qtd alunos",
            "Tipo turma",
            "Instituto responsável",
            "Tipo sala",
            "Período",
        ]
    )
    courses.rename(
        columns={
            "Código único turma": "course_class_id",
            "Código disciplina": "course_id",
            "Nome disciplina": "course_name",
            "Curso": "graduation_course",
            "Qtd de créditos": "credits",
            "Dia da semana": "day",
            "Horário": "time",
            "Tipo disciplina": "course_type",
            "Qtd alunos": "capacity",
            "Tipo turma": "class_type",
            "Instituto responsável": "responsable_institute",
            "Tipo sala": "classroom_type",
            "Período": "term",
        },
        inplace=True,
    )
    courses.set_index("course_class_id", inplace=True)

    return courses


@cache_to_csv("cache/get_elective_courses.csv", refresh_time=settings.APP_CACHE_TTL)
def get_elective_courses():
    """
    Retrieves elective courses from a Google Sheet and returns them as a DataFrame.
    This function reads data from the "disciplinas_eletivas" sheet in the Google Spreadsheet
    specified by `settings.SAMPLE_SPREADSHEET_ID`. It filters the courses that are marked
    for allocation ("Alocar" == "TRUE") and selects specific columns to be included in the
    resulting DataFrame. The columns are then renamed to more descriptive names and the
    DataFrame is indexed by the unique course class ID.
    Returns:
        pandas.DataFrame: A DataFrame containing elective courses with the following columns:
            - course_class_id: Unique identifier for the course class
            - course_id: Identifier for the course
            - credits: Number of credits for the course
            - knowledge_area: Knowledge area or profile of the course
            - course_type: Type of the course
            - class_type: Type of the class
            - term: Term or period of the course
            - graduation_course: Graduation course to which the course belongs
    """

    page_name = "disciplinas_eletivas!A:S"
    df = read_google_sheet_to_dataframe(settings.SAMPLE_SPREADSHEET_ID, page_name)

    courses = df.loc[df["Alocar"] == "TRUE"].filter(
        [
            "Código único turma",
            "Código disciplina",
            "Qtd de créditos",
            "Perfil",
            "Tipo disciplina",
            "Tipo turma",
            "Período",
            "Curso",
        ]
    )
    courses.rename(
        columns={
            "Código único turma": "course_class_id",
            "Código disciplina": "course_id",
            "Qtd de créditos": "credits",
            "Perfil": "knowledge_area",
            "Tipo disciplina": "course_type",
            "Tipo turma": "class_type",
            "Período": "term",
            "Curso": "graduation_course",
        },
        inplace=True,
    )
    courses.set_index("course_class_id", inplace=True)

    return courses


@cache_to_csv("cache/get_substitute_professor.csv", refresh_time=settings.APP_CACHE_TTL)
def get_substitute_professor():
    """
    Retrieves a DataFrame of substitute professors from a Google Sheet.
    This function reads data from a Google Sheet specified by the SAMPLE_SPREADSHEET_ID
    in the settings. It filters the data to include only professors who are available
    for allocation (where the "Alocar" column is "TRUE") and belong to the "PS" category.
    The relevant columns are renamed for clarity.
    Returns:
        pandas.DataFrame: A DataFrame containing the substitute professors with columns:
        - "qualified_courses": Qualified courses the professor can teach
        - "expertise": Expertise area of the professor
        - "category": Category of the professor
    """

    page_name = "professores!A:S"
    df = read_google_sheet_to_dataframe(settings.SAMPLE_SPREADSHEET_ID, page_name)

    professors_availables = df.loc[df["Alocar"] == "TRUE"].filter(
        ["Nome curto", "Disciplinas aptas", "Área de conhecimento", "Categoria"]
    )
    professors_availables.rename(
        columns={
            "Nome curto": "professor",
            "Disciplinas aptas": "qualified_courses",
            "Área de conhecimento": "expertise",
            "Categoria": "category",
        },
        inplace=True,
    )
    professors_availables.set_index("professor", inplace=True)

    substitute = professors_availables.loc[(professors_availables["category"] == "PS")]

    return substitute


@cache_to_csv("cache/get_permanent_professors.csv", refresh_time=settings.APP_CACHE_TTL)
def get_permanent_professors():
    """
    Retrieves a DataFrame of permanent professors from a Google Sheet.
    This function reads data from a Google Sheet specified by the SAMPLE_SPREADSHEET_ID
    in the settings. It filters the data to include only professors who are available
    for allocation (where the "Alocar" column is "TRUE") and do not belong to the "PS" or "EX" categories.
    The relevant columns are renamed for clarity.
    Returns:
        pandas.DataFrame: A DataFrame containing the permanent professors with columns:
        - "qualified_courses": Qualified courses the professor can teach
        - "expertise": Expertise area of the professor
        - "category": Category of the professor
    """
    page_name = "professores!A:S"
    df = read_google_sheet_to_dataframe(settings.SAMPLE_SPREADSHEET_ID, page_name)

    professors_availables = df.loc[df["Alocar"] == "TRUE"].filter(
        ["Nome curto", "Disciplinas aptas", "Área de conhecimento", "Categoria"]
    )
    professors_availables.rename(
        columns={
            "Nome curto": "professor",
            "Disciplinas aptas": "qualified_courses",
            "Área de conhecimento": "expertise",
            "Categoria": "category",
        },
        inplace=True,
    )
    professors_availables.set_index("professor", inplace=True)

    permanent = professors_availables.loc[
        (~professors_availables["category"].isin(["PS", "EX"]))
    ]

    return permanent


def get_professors():
    return get_permanent_professors(), get_substitute_professor()


@cache_to_csv("cache/get_manual_allocation.csv", refresh_time=settings.APP_CACHE_TTL)
def get_manual_allocation():
    """
    Retrieves manual allocation data from a Google Sheet and returns it as a DataFrame.
    This function reads data from the "alocacao_manual" sheet in the Google Spreadsheet
    specified by `settings.SAMPLE_SPREADSHEET_ID`. It selects specific columns to be included
    in the resulting DataFrame. The columns are then renamed to more descriptive names and the
    DataFrame is indexed by the unique course class ID.
    Returns:
        pandas.DataFrame: A DataFrame containing manual allocation data with the following columns:
            - professor: Name of the professor
            - course_class_id: Unique identifier for the course class
            - course_id: Identifier for the course
            - course_name: Name of the course
            - graduation_course: Graduation course to which the course belongs
            - credits: Number of credits for the course
            - course_type: Type of the course
            - day: Day of the week
            - time: Time of the class
            - capacity: Number of students
            - class_type: Type of the class
            - responsable_institute: Responsible institute
            - classroom_type: Type of classroom
            - term: Term or period of the course
    """
    page_name = "alocacao_manual!A:S"

    df = read_google_sheet_to_dataframe(settings.SAMPLE_SPREADSHEET_ID, page_name)

    manual_allocation = df.filter(
        [
            "Nome curto professor",
            "Código único turma",
            "Código disciplina",
            "Nome disciplina",
            "Curso",
            "Qtd de créditos",
            "Tipo disciplina",
            "Dia da semana",
            "Horário",
            "Qtd alunos",
            "Tipo turma",
            "Instituto responsável",
            "Tipo sala",
            "Período",
        ]
    )
    manual_allocation.rename(
        columns={
            "Nome curto professor": "professor",
            "Código único turma": "course_class_id",
            "Código disciplina": "course_id",
            "Nome disciplina": "course_name",
            "Curso": "graduation_course",
            "Qtd de créditos": "credits",
            "Tipo disciplina": "course_type",
            "Dia da semana": "day",
            "Horário": "time",
            "Qtd alunos": "capacity",
            "Tipo turma": "class_type",
            "Instituto responsável": "responsable_institute",
            "Tipo sala": "classroom_type",
            "Período": "term",
        },
        inplace=True,
    )
    manual_allocation.set_index("course_class_id", inplace=True)

    return manual_allocation
