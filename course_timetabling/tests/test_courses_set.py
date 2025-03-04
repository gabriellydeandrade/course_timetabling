from unittest import TestCase, main, skip
from unittest.mock import patch
import sys
import os

from functools import wraps

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # FIXME quero corrigir de outra forma

def mock_decorator(*args, **kwargs):
    """Decorate by doing nothing."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    return decorator

patch('cache_pandas.cache_to_csv', mock_decorator).start()

from database.service_google_sheet import (
    get_required_courses,
    get_elective_courses,
)
from database.transform_data import transform_courses_to_dict
from database.construct_sets import get_courses_set, get_elective_courses_set

import pandas as pd


class TestGetRequiredCoursesFromGoogleSheets(TestCase):

    def setUp(self) -> None:
        return super().setUp()

    @patch("database.service_google_sheet.read_google_sheet_to_dataframe")
    def test_get_required_courses_with_correct_params(self, mock_read_google_sheet):
        mock_read_google_sheet.return_value = pd.DataFrame(
            {
                "Alocar": ["TRUE", "TRUE"],
                "Código único turma": [
                    "OBG-BCC1-1",
                    "OBG-BCC1-2",
                ],
                "Código disciplina": ["ICP131", "ICP123"],
                "Nome disciplinas": ["Programação de Computadores I", "Prog II"],
                "Qtd de créditos": ["4", "4"],
                "Dia da semana": ["SEG,QUA", "TER,QUI"],
                "Horário": ["13:00-15:00,08:00-10:00", "15:00-17:00"],
                "Tipo disciplina": ["OBG", "SVC"],
            }
        )
        result_courses = get_required_courses()

        expected_courses = pd.DataFrame(
            {
                "course_id": ["ICP131", "ICP123"],
                "credits": ["4", "4"],
                "day": ["SEG,QUA", "TER,QUI"],
                "time": ["13:00-15:00,08:00-10:00", "15:00-17:00"],
                "course_type": ["OBG", "SVC"],
            },
            index=[
                "OBG-BCC1-1",
                "OBG-BCC1-2",
            ],
        )
        expected_courses.index.name = "course_class_id"

        pd.testing.assert_frame_equal(result_courses, expected_courses)


class TestTransformRequiredCourses(TestCase):

    def test_treat_required_courses_with_correct_params(self):
        course = pd.DataFrame(
            {
                "course_id": ["ICP131,ICP222", "ICP123"],
                "credits": ["4", "4"],
                "day": ["SEG,QUA", "TER,QUI"],
                "time": ["13:00-15:00,08:00-10:00", "15:00-17:00"],
                "course_type": ["OBG", "SVC"],
            },
            index=[
                "OBG-BCC1-1",
                "OBG-BCC1-2",
            ],
        )
        course.index.name = "course_class_id"

        result = transform_courses_to_dict(course)

        expected_result = {
            "OBG-BCC1-1": {
                "course_id": "ICP131,ICP222",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00,08:00-10:00",
                "course_type": "OBG",
            },
            "OBG-BCC1-2": {
                "course_id": "ICP123",
                "credits": 4,
                "day": "TER,QUI",
                "time": "15:00-17:00",
                "course_type": "SVC",
            },
        }

        self.assertDictEqual(result, expected_result)


class TestGetCoursesSet(TestCase):

    @patch("database.service_google_sheet.read_google_sheet_to_dataframe")
    def test_get_courses_set_with_no_manual_allocation(self, mock_read_google_sheet):
        mock_read_google_sheet.return_value = pd.DataFrame(
            {
                "Alocar": ["TRUE", "TRUE"],
                "Código único turma": [
                    "OBG-BCC1-1",
                    "OBG-BCC1-2",
                ],
                "Código disciplina": ["ICP131", "ICP123"],
                "Nome disciplinas": ["Programação de Computadores I", "Prog II"],
                "Qtd de créditos": ["4", "4"],
                "Dia da semana": ["SEG,QUA", "TER,QUI"],
                "Horário": ["13:00-15:00,08:00-10:00", "15:00-17:00"],
                "Tipo disciplina": ["OBG", "SVC"],
            }
        )

        manual_allocation_set = dict()
        result = get_courses_set(manual_allocation_set)

        expected_result = {
            "OBG-BCC1-1": {
                "course_id": "ICP131",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00,08:00-10:00",
                "course_type": "OBG",
            },
            "OBG-BCC1-2": {
                "course_id": "ICP123",
                "credits": 4,
                "day": "TER,QUI",
                "time": "15:00-17:00",
                "course_type": "SVC",
            },
        }

        self.assertDictEqual(result, expected_result)

    @patch("database.service_google_sheet.read_google_sheet_to_dataframe")
    def test_get_courses_set_with_manual_allocation(self, mock_read_google_sheet):
        mock_read_google_sheet.return_value = pd.DataFrame(
            {
                "Alocar": ["TRUE", "TRUE"],
                "Código único turma": [
                    "OBG-BCC1-1",
                    "OBG-BCC1-2",
                ],
                "Código disciplina": ["ICP131", "ICP123"],
                "Nome disciplinas": ["Programação de Computadores I", "Prog II"],
                "Qtd de créditos": ["4", "4"],
                "Dia da semana": ["SEG,QUA", "TER,QUI"],
                "Horário": ["13:00-15:00,08:00-10:00", "15:00-17:00"],
                "Tipo disciplina": ["OBG", "SVC"],
            }
        )

        manual_allocation_set = {
            "OPT-BCC1-1": {
                "course_id": "ICPXXX",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00,08:00-10:00",
                "course_type": "OPT",
            }
        }
        result = get_courses_set(manual_allocation_set)

        expected_result = {
            "OBG-BCC1-1": {
                "course_id": "ICP131",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00,08:00-10:00",
                "course_type": "OBG",
            },
            "OBG-BCC1-2": {
                "course_id": "ICP123",
                "credits": 4,
                "day": "TER,QUI",
                "time": "15:00-17:00",
                "course_type": "SVC",
            },
            "OPT-BCC1-1": {
                "course_id": "ICPXXX",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00,08:00-10:00",
                "course_type": "OPT",
            },
        }

        self.assertDictEqual(result, expected_result)

    @patch("database.service_google_sheet.read_google_sheet_to_dataframe")
    def test_get_courses_set_only_if_manual_allocation_is_optional(
        self, mock_read_google_sheet
    ):
        mock_read_google_sheet.return_value = pd.DataFrame(
            {
                "Alocar": ["TRUE", "TRUE"],
                "Código único turma": [
                    "OBG-BCC1-1",
                    "OBG-BCC1-2",
                ],
                "Código disciplina": ["ICP131", "ICP123"],
                "Nome disciplinas": ["Programação de Computadores I", "Prog II"],
                "Qtd de créditos": ["4", "4"],
                "Dia da semana": ["SEG,QUA", "TER,QUI"],
                "Horário": ["13:00-15:00,08:00-10:00", "15:00-17:00"],
                "Tipo disciplina": ["OBG", "SVC"],
            }
        )

        manual_allocation_set = {
            "OBG-BCC1-1": {
                "course_id": "ICPXXX",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00,08:00-10:00",
                "course_type": "OBG",
            },
            "OBG-BCC1-1": {
                "course_id": "ICPXXX",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00,08:00-10:00",
                "course_type": "SVC",
            },
            "OPT-BCC1-1": {
                "course_id": "ICPXXX",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00,08:00-10:00",
                "course_type": "OPT",
            },
        }
        result = get_courses_set(manual_allocation_set)

        expected_result = {
            "OBG-BCC1-1": {
                "course_id": "ICP131",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00,08:00-10:00",
                "course_type": "OBG",
            },
            "OBG-BCC1-2": {
                "course_id": "ICP123",
                "credits": 4,
                "day": "TER,QUI",
                "time": "15:00-17:00",
                "course_type": "SVC",
            },
            "OPT-BCC1-1": {
                "course_id": "ICPXXX",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00,08:00-10:00",
                "course_type": "OPT",
            },
        }

        self.assertDictEqual(result, expected_result)


class TestGetElectiveCoursesFromGoogleSheets(TestCase):

    def setUp(self) -> None:
        return super().setUp()

    @patch("database.service_google_sheet.read_google_sheet_to_dataframe")
    def test_get_elective_courses_with_correct_params(self, mock_read_google_sheet):
        mock_read_google_sheet.return_value = pd.DataFrame(
            {
                "Alocar": ["TRUE", "TRUE"],
                "Código único turma": [
                    "OPT-BCC1-1",
                    "OPT-MAI-61",
                ],
                "Código disciplina": ["ICP777", "ICP999"],
                "Perfil": ["CD,ED", "CC"],
                "Nome disciplinas": ["Dados em vetor", "Prog III"],
                "Qtd de créditos": ["4", "4"],
                "Tipo disciplina": ["OPT", "OPT"],
                "Tipo turma": ["Gradução", "Mestrado"],
            }
        )
        result_courses = get_elective_courses()

        expected_courses = pd.DataFrame(
            {
                "course_id": ["ICP777", "ICP999"],
                "credits": ["4", "4"],
                "knowledge_area": ["CD,ED", "CC"],
                "course_type": ["OPT", "OPT"],
                "class_type": ["Gradução", "Mestrado"],
            },
            index=[
                "OPT-BCC1-1",
                "OPT-MAI-61",
            ],
        )
        expected_courses.index.name = "course_class_id"

        pd.testing.assert_frame_equal(result_courses, expected_courses)


class TestTransformElectiveCourses(TestCase):

    def test_treat_elective_courses_with_correct_params(self):
        course = pd.DataFrame(
            {
                "course_id": ["ICP131,ICP222", "ICP888"],
                "credits": ["4", "4"],
                "knowledge_area": ["ED", "CC"],
                "course_type": ["OPT", "OPT"],
                "class_type": ["Gradução", "Mestrado"],
            },
            index=[
                "OPT-BCC1-1",
                "OPT-BCC1-2",
            ],
        )
        course.index.name = "course_class_id"

        result = transform_courses_to_dict(course)

        expected_result = {
            "OPT-BCC1-1": {
                "course_id": "ICP131,ICP222",
                "credits": 4,
                "knowledge_area": "ED",
                "course_type": "OPT",
                "class_type": "Gradução",
            },
            "OPT-BCC1-2": {
                "course_id": "ICP888",
                "credits": 4,
                "knowledge_area": "CC",
                "course_type": "OPT",
                "class_type": "Mestrado",
            },
        }

        self.assertDictEqual(result, expected_result)


class TestGetElectiveCoursesSet(TestCase):

    @patch("database.service_google_sheet.read_google_sheet_to_dataframe")
    def test_get_elective_courses_set(self, mock_read_google_sheet):
        mock_read_google_sheet.return_value = pd.DataFrame(
            {
                "Alocar": ["TRUE", "TRUE"],
                "Código único turma": [
                    "OPT-BCC1-1",
                    "OPT-MAI-61",
                ],
                "Código disciplina": ["ICP777", "ICP999"],
                "Perfil": ["CD,ED", "CC"],
                "Nome disciplinas": ["Dados em vetor", "Prog III"],
                "Qtd de créditos": ["4", "4"],
                "Tipo disciplina": ["OPT", "OPT"],
                "Tipo turma": ["Gradução", "Mestrado"],
            }
        )

        result = get_elective_courses_set()

        expected_result = {
            "OPT-BCC1-1": {
                "course_id": "ICP777",
                "credits": 4,
                "knowledge_area": "CD,ED",
                "course_type": "OPT",
                "class_type": "Gradução",
            },
            "OPT-MAI-61": {
                "course_id": "ICP999",
                "credits": 4,
                "knowledge_area": "CC",
                "course_type": "OPT",
                "class_type": "Mestrado",
            },
        }

        self.assertDictEqual(result, expected_result)


if __name__ == "__main__":
    main()
