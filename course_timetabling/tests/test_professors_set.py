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


patch("cache_pandas.cache_to_csv", mock_decorator).start()

from database.construct_sets import get_professors_set
from database.service_google_sheet import get_professors
from database.transform_data import (
    transform_professors_to_dict,
)

import pandas as pd


class TestGetProfessorsFromGoogleSheets(TestCase):

    def setUp(self) -> None:
        return super().setUp()

    @patch("database.service_google_sheet.read_google_sheet_to_dataframe")
    def test_get_professors_with_correct_params(self, mock_read_google_sheet):
        mock_read_google_sheet.return_value = pd.DataFrame(
            {
                "Alocar": ["TRUE", "TRUE", "TRUE"],
                "Nome curto": [
                    "Professor 1",
                    "Professor 2",
                    "Professor 3",
                ],
                "Disciplinas aptas": ["ICP145,ICP616", "", ""],
                "Área de conhecimento": ["ED,ES,H", "ED,CD", ""],
                "Categoria": ["PP", "PP", "PS"],
            }
        )
        result_permanent, result_substitute = get_professors()

        expected_permanent = pd.DataFrame(
            {
                "qualified_courses": ["ICP145,ICP616", ""],
                "expertise": ["ED,ES,H", "ED,CD"],
                "category": ["PP", "PP"],
            },
            index=["Professor 1", "Professor 2"],
        )
        expected_permanent.index.name = "professor"

        expected_substitute = pd.DataFrame(
            {
                "qualified_courses": [""],
                "expertise": [""],
                "category": ["PS"],
            },
            index=["Professor 3"],
        )
        expected_substitute.index.name = "professor"

        pd.testing.assert_frame_equal(result_permanent, expected_permanent)
        pd.testing.assert_frame_equal(result_substitute, expected_substitute)

    @patch("database.service_google_sheet.read_google_sheet_to_dataframe")
    def test_get_professors_filtering_allocation_equals_true(
        self, mock_read_google_sheet
    ):
        mock_read_google_sheet.return_value = pd.DataFrame(
            {
                "Alocar": ["TRUE", "TRUE", "TRUE", "FALSE"],
                "Nome curto": [
                    "Professor 1",
                    "Professor 2",
                    "Professor 3",
                    "FULANO",
                ],
                "Disciplinas aptas": ["ICP145,ICP616", "", "", ""],
                "Área de conhecimento": ["ED,ES,H", "ED,CD", "", ""],
                "Categoria": ["PP", "PP", "PS", "PP"],
            }
        )

        result_permanent, result_substitute = get_professors()

        expected_permanent = pd.DataFrame(
            {
                "qualified_courses": ["ICP145,ICP616", ""],
                "expertise": ["ED,ES,H", "ED,CD"],
                "category": ["PP", "PP"],
            },
            index=["Professor 1", "Professor 2"],
        )
        expected_permanent.index.name = "professor"

        expected_substitute = pd.DataFrame(
            {
                "qualified_courses": [""],
                "expertise": [""],
                "category": ["PS"],
            },
            index=["Professor 3"],
        )
        expected_substitute.index.name = "professor"

        pd.testing.assert_frame_equal(result_permanent, expected_permanent)
        pd.testing.assert_frame_equal(result_substitute, expected_substitute)


class TestTransformProfessors(TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def test_treat_permanent_professors_with_correct_params(self):
        permanent_professors = pd.DataFrame(
            {
                "qualified_courses": ["ICP145,ICP616", ""],
                "expertise": ["ED,ES,H", "ED,CD"],
                "category": ["PP", "PP"],
            },
            index=["Professor 1", "Professor 2"],
        )
        permanent_professors.index.name = "professor"

        result = transform_professors_to_dict(permanent_professors)

        expected_result = {
            "Professor 1": {
                "qualified_courses": ["ICP145", "ICP616"],
                "expertise": ["ED", "ES", "H"],
                "category": "PP",
            },
            "Professor 2": {
                "qualified_courses": [],
                "expertise": ["ED", "CD"],
                "category": "PP",
            },
        }

        self.assertDictEqual(result, expected_result)


class TestGetProfessorsSet(TestCase):

    @patch("database.service_google_sheet.read_google_sheet_to_dataframe")
    def test_get_professors_set_correctly(self, mock_read_google_sheet):
        mock_read_google_sheet.return_value = pd.DataFrame(
            {
                "Alocar": ["TRUE", "TRUE", "TRUE"],
                "Nome curto": [
                    "Professor 1",
                    "Professor 2",
                    "Professor 3",
                ],
                "Disciplinas aptas": ["ICP145,ICP616", "", ""],
                "Área de conhecimento": ["ED,ES,H", "ED,CD", ""],
                "Categoria": ["PP", "PP", "PS"],
            }
        )

        result = get_professors_set()

        expected_substitute = {
            "Professor 3": {
                "qualified_courses": [],
                "expertise": [],
                "category": "PS",
            }
        }

        expected_permanent = {
            "Professor 1": {
                "qualified_courses": ["ICP145", "ICP616"],
                "expertise": ["ED", "ES", "H"],
                "category": "PP",
            },
            "Professor 2": {
                "qualified_courses": [],
                "expertise": ["ED", "CD"],
                "category": "PP",
            },
        }

        professor_dummy = {
            "DUMMY": {
                "qualified_courses": ["*"],
                "expertise": ["*"],
                "category": "DUMMY",
            }
        }

        expected_result = (expected_permanent, expected_substitute, professor_dummy)

        self.assertEqual(result, expected_result)

    @patch("database.service_google_sheet.read_google_sheet_to_dataframe")
    def test_if_math_courses_are_added_to_cc_professor_expertise(
        self, mock_read_google_sheet
    ):
        mock_read_google_sheet.return_value = pd.DataFrame(
            {
                "Alocar": ["TRUE", "TRUE"],
                "Nome curto": ["Professor 1", "Professor 4"],
                "Disciplinas aptas": ["ICP145,ICP616", "ICPXXX"],
                "Área de conhecimento": ["ED,ES,H", "CC"],
                "Categoria": ["PP", "PP"],
            }
        )

        result = get_professors_set()

        cc_math_courses = ["ICP231", "MAW123", "ICP478"]

        expected_permanent = {
            "Professor 1": {
                "qualified_courses": ["ICP145", "ICP616"],
                "expertise": ["ED", "ES", "H"],
                "category": "PP",
            },
            "Professor 4": {
                "qualified_courses": ["ICPXXX"] + cc_math_courses,
                "expertise": ["CC"],
                "category": "PP",
            },
        }

        professor_dummy = {
            "DUMMY": {
                "qualified_courses": ["*"],
                "expertise": ["*"],
                "category": "DUMMY",
            }
        }

        expected_substitute = {}

        expected_result = (expected_permanent, expected_substitute, professor_dummy)

        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    main()
