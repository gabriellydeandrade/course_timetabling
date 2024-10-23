from unittest import TestCase, main, skip
from unittest.mock import patch
import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # FIXME quero corrigir de outra forma

from database.service_google_sheet import (
    get_manual_allocation,
    get_required_courses,
    get_elective_courses,
)
from database.transform_data import transform_courses_to_dict
from database.construct_sets import get_courses_set

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
    def test_get_courses_set_correctly(self, mock_read_google_sheet):
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

        result = get_courses_set()

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


class TestGetManuelAllocationFromGoogleSheets(TestCase):
    @patch("database.service_google_sheet.read_google_sheet_to_dataframe")
    def test_get_manual_allocation(self, mock_read_google_sheet):
        mock_data = pd.DataFrame(
            {
                "Nome curto professor": ["Prof1", "Prof2"],
                "Código único turma": ["Class1", "Class2"],
                "Código disciplina": ["Course1", "Course2"],
                "Qtd de créditos": [4, 2],
                "Dia da semana": ["SEG,QUA", "TER"],
                "Horário": ["08:00-10:00", "10:00-12:00"],
            }
        )

        mock_read_google_sheet.return_value = mock_data

        result = get_manual_allocation()

        expected_data = pd.DataFrame(
            {
                "course_class_id": ["Class1", "Class2"],
                "course_id": ["Course1", "Course2"],
                "credits": [4, 2],
                "day": ["SEG,QUA", "TER"],
                "time": ["08:00-10:00", "10:00-12:00"],
            },
            index=["Prof1", "Prof2"],
        )
        expected_data.index.name = "professor"


        pd.testing.assert_frame_equal(result, expected_data)


if __name__ == "__main__":
    main()
