from unittest import TestCase, main
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
    get_manual_allocation,
)
from database.transform_data import transform_courses_to_dict


import pandas as pd


class TestGetManualAllocationFromGoogleSheets(TestCase):
    @patch("database.service_google_sheet.read_google_sheet_to_dataframe")
    def test_get_manual_allocation(self, mock_read_google_sheet):
        mock_data = pd.DataFrame(
            {
                "Nome curto professor": ["Prof1", "Prof2", "Prof2"],
                "Código único turma": ["Class1", "Class2", "Class3"],
                "Código disciplina": ["Course1", "Course2", "Course3"],
                "Qtd de créditos": [4, 2, 2],
                "Tipo disciplina": ["OBG", "OPT", "OPT"],
                "Dia da semana": ["SEG,QUA", "TER", "QUI"],
                "Horário": ["08:00-10:00", "10:00-12:00", "10:00-12:00"],
            }
        )

        mock_read_google_sheet.return_value = mock_data

        result = get_manual_allocation()

        expected_data = pd.DataFrame(
            {
                "professor": ["Prof1", "Prof2", "Prof2"],
                "course_id": ["Course1", "Course2", "Course3"],
                "credits": [4, 2, 2],
                "course_type": ["OBG", "OPT", "OPT"],
                "day": ["SEG,QUA", "TER", "QUI"],
                "time": ["08:00-10:00", "10:00-12:00", "10:00-12:00"],
            },
            index=["Class1", "Class2", "Class3"],
        )
        expected_data.index.name = "course_class_id"

        pd.testing.assert_frame_equal(result, expected_data)


class TestTransformManualAllocation(TestCase):

    def test_treat_required_courses_with_correct_params(self):
        manual_allocation = pd.DataFrame(
            {
                "professor": ["Prof1", "Prof2", "Prof2"],
                "course_id": ["Course1", "Course2", "Course3"],
                "credits": [4, 2, 2],
                "day": ["SEG,QUA", "TER", "QUI"],
                "time": ["08:00-10:00", "10:00-12:00", "10:00-12:00"],
            },
            index=["Class1", "Class2", "Class3"],
        )
        manual_allocation.index.name = "coursse_class_id"

        result = transform_courses_to_dict(manual_allocation)
        expected_result = {
            "Class1": {
                "professor": "Prof1",
                "course_id": "Course1",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "08:00-10:00",
            },
            "Class2": {
                "professor": "Prof2",
                "course_id": "Course2",
                "credits": 2,
                "day": "TER",
                "time": "10:00-12:00",
            },
            "Class3": {
                "professor": "Prof2",
                "course_id": "Course3",
                "credits": 2,
                "day": "QUI",
                "time": "10:00-12:00",
            },
        }

        self.assertDictEqual(result, expected_result)


if __name__ == "__main__":
    main()
