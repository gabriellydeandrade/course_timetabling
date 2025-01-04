import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from course_timetabling.settings import DUMMY_COEFFICIENT
from main import CourseTimetabling


class TestInitializeVariablesAndCoefficients(unittest.TestCase):

    @patch("utils.utils.get_course_schedule")
    def setUp(self, mock_get_schedule) -> None:
        patch("utils.utils.save_results_to_csv").start()

        professor_permanent = {
            "Prof1": {
                "qualified_courses": ["ICP131"],
                "expertise": ["ED", "ES", "H"],
                "category": "PP",
            },
        }
        professor_substitute = {
            "Prof2": {
                "qualified_courses": [],
                "expertise": ["ED", "CD"],
                "category": "PS",
            },
        }
        professor_dummy = {
            "DUMMY": {
                "qualified_courses": ["*"],
                "expertise": ["*"],
                "category": "DUMMY",
            },
        }
        self.PROFESSORS = professor_permanent | professor_substitute | professor_dummy
        self.COURSES = {
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
                "course_type": "OBG",
            },
        }
        mock_get_schedule.side_effect = lambda courses, course: (
            ("SEG", "13:00-15:00") if course == "OBG-BCC1-1" else ("TER", "15:00-17:00")
        )

        self.timetabling = CourseTimetabling(
            self.PROFESSORS,
            professor_permanent,
            professor_substitute,
            self.COURSES,
            {},
        )
        self.timetabling.initialize_variables_and_coefficients()
        return super().setUp()

    def test_set_coefficient_if_professor_is_qualified_for_class(self):

        expected_coefficient = 10

        self.assertIn("Prof1", self.timetabling.EAP_coefficient)
        self.assertIn("OBG-BCC1-1", self.timetabling.EAP_coefficient["Prof1"])

        for day, value in self.timetabling.EAP_coefficient["Prof1"]["OBG-BCC1-1"].items():
            time = list(value.keys())[0]
            self.assertEqual(
                self.timetabling.EAP_coefficient["Prof1"]["OBG-BCC1-1"][day][time],
                expected_coefficient,
            )

        self.assertIn("OBG-BCC1-1", self.timetabling.X_variables["Prof1"])

    def test_set_coefficient_to_zero_if_professor_is_not_qualified_for_class(self):

        self.assertIn("Prof1", self.timetabling.EAP_coefficient)
        self.assertIn("OBG-BCC1-2", self.timetabling.EAP_coefficient["Prof1"])

        for day, value in self.timetabling.EAP_coefficient["Prof1"]["OBG-BCC1-2"].items():
            time = list(value.keys())[0]
            self.assertEqual(
                self.timetabling.EAP_coefficient["Prof1"]["OBG-BCC1-2"][day][time], 0
            )

        self.assertIn("OBG-BCC1-2", self.timetabling.X_variables["Prof1"])

    def test_set_coefficient_specific_if_professor_is_dummy(self):

        self.assertIn("DUMMY", self.timetabling.EAP_coefficient)
        self.assertIn("OBG-BCC1-1", self.timetabling.EAP_coefficient["DUMMY"])
        self.assertIn("OBG-BCC1-2", self.timetabling.EAP_coefficient["DUMMY"])

        for day, value in self.timetabling.EAP_coefficient["DUMMY"]["OBG-BCC1-1"].items():
            time = list(value.keys())[0]
            self.assertEqual(
                self.timetabling.EAP_coefficient["DUMMY"]["OBG-BCC1-1"][day][time], DUMMY_COEFFICIENT
            )

        for day, value in self.timetabling.EAP_coefficient["DUMMY"]["OBG-BCC1-2"].items():
            time = list(value.keys())[0]
            self.assertEqual(
                self.timetabling.EAP_coefficient["DUMMY"]["OBG-BCC1-2"][day][time], DUMMY_COEFFICIENT
            )

        self.assertIn("OBG-BCC1-1", self.timetabling.X_variables["DUMMY"])
        self.assertIn("OBG-BCC1-2", self.timetabling.X_variables["DUMMY"])


class TestAddCreditSlackVariables(unittest.TestCase):

    def setUp(self) -> None:
        self.timetabling = CourseTimetabling(
            ["Prof1", "Prof2"], ["Prof1"], ["Prof2"], {}, {}
        )
        self.timetabling.add_credit_slack_variables()
        return super().setUp()

    def test_add_credit_slack_variables(self):
        self.assertIn("Prof1", self.timetabling.PP_slack_variables)

    def test_add_credit_slack_variables_only_for_permanent_professors(self):
        self.assertIn("Prof1", self.timetabling.PP_slack_variables)
        self.assertNotIn("Prof2", self.timetabling.PP_slack_variables)


class TestModelCourseTimetabling(unittest.TestCase):

    def setUp(self) -> None:

        self.PERMANENT_PROFESSORS = {
            "Adriana Vivacqua": {
                "qualified_courses": ["ICP131"],
                "expertise": ["ED", "ES", "H"],
                "category": "PP",
            },
            "Daniel Sadoc": {
                "qualified_courses": ["ICP132"],
                "expertise": ["ED", "CD"],
                "category": "PP",
            },
        }
        self.PROFESSORS = {
            **self.PERMANENT_PROFESSORS,
            "DUMMY": {
                "qualified_courses": ["*"],
                "expertise": ["*"],
                "category": "DUMMY",
            },
        }
        self.COURSES = {
            "OBG-BCC1-1": {
                "course_id": "ICP131",
                "course_name": "Programação de Computadores I",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00,08:00-10:00",
                "course_type": "OBG",
                "class_type": "Gradução",
                "capacity": 40,
                "responsable_institute": "IC",
                "classroom_type": "Sala",
                "term": 1
            },
            "OBG-BCC1-2": {
                "course_id": "ICP132",
                "course_name": "Processo de Software",
                "credits": 4,
                "day": "TER,QUI",
                "time": "15:00-17:00",
                "course_type": "OBG",
                "class_type": "Gradução",
                "capacity": 30,
                "responsable_institute": "IC",
                "classroom_type": "Sala",
                "term": 1
            },
            "OPT-BCC1-3": {
                "course_id": "IPCXXX",
                "course_name": "Eletiva",
                "credits": 4,
                "day": "NÃO DEFINIDO",
                "time": "NÃO DEFINIDO",
                "course_type": "OPT",
                "class_type": "Gradução",
                "capacity": 30,
                "responsable_institute": "IC",
                "classroom_type": "Sala",
                "term": None
            },
        }

        return super().setUp()

    def test_if_allocates_all_required_courses_qualified_for_professors(self):
        timetabling = CourseTimetabling(
            professors=self.PROFESSORS,
            permanent_professors=self.PERMANENT_PROFESSORS,
            substitute_professors=[],
            courses=self.COURSES,
            manual_allocation={},
        )
        timetabling.initialize_variables_and_coefficients()
        timetabling.add_credit_slack_variables()
        timetabling.add_constraints()
        timetabling.set_objective()
        timetabling.optimize()

        result, result_value = timetabling.generate_results()

        expected_result = [
            "Adriana Vivacqua_OBG-BCC1-1_SEG,QUA_13:00-15:00,08:00-10:00/1.0",
            "Daniel Sadoc_OBG-BCC1-2_TER,QUI_15:00-17:00/1.0",
        ]

        for item in expected_result:
            self.assertIn(item, result)

        self.assertLessEqual(result_value, 0)

    def test_if_allocates_all_required_courses_for_dummy_professors(self):

        self.PERMANENT_PROFESSORS = {
            "Adriana Vivacqua": {
                "qualified_courses": [],
                "expertise": ["ED", "ES", "H"],
                "category": "PP",
            },
            "Daniel Sadoc": {
                "qualified_courses": [],
                "expertise": ["ED", "CD"],
                "category": "PP",
            },
        }
        self.PROFESSORS = {
            **self.PERMANENT_PROFESSORS,
            "DUMMY": {
                "qualified_courses": ["*"],
                "expertise": ["*"],
                "category": "DUMMY",
            },
        }

        timetabling = CourseTimetabling(
            professors=self.PROFESSORS,
            permanent_professors=self.PERMANENT_PROFESSORS,
            substitute_professors=[],
            courses=self.COURSES,
            manual_allocation={},
        )
        timetabling.initialize_variables_and_coefficients()
        timetabling.add_credit_slack_variables()
        timetabling.add_constraints()
        timetabling.set_objective()
        timetabling.optimize()

        result, result_value = timetabling.generate_results()

        expected_result = [
            "DUMMY_OBG-BCC1-1_SEG,QUA_13:00-15:00,08:00-10:00/1.0",
            "DUMMY_OBG-BCC1-2_TER,QUI_15:00-17:00/1.0",
        ]

        for item in expected_result:
            self.assertIn(item, result)

        self.assertLessEqual(result_value, 0)

    def test_it_professor_received_a_penalty_for_less_credit(self):

        timetabling = CourseTimetabling(
            professors=self.PROFESSORS,
            permanent_professors=self.PERMANENT_PROFESSORS,
            substitute_professors=[],
            courses=self.COURSES,
            manual_allocation={},
        )
        timetabling.initialize_variables_and_coefficients()
        timetabling.add_credit_slack_variables()
        timetabling.add_constraints()
        timetabling.set_objective()
        timetabling.optimize()

        result, result_value = timetabling.generate_results()

        expected_result = [
            "Adriana Vivacqua_OBG-BCC1-1_SEG,QUA_13:00-15:00,08:00-10:00/1.0",
            "Daniel Sadoc_OBG-BCC1-2_TER,QUI_15:00-17:00/1.0",
            "DUMMY_OPT-BCC1-3_NÃO DEFINIDO_NÃO DEFINIDO/1.0",  # FIXME não quero ter professor dummy associados a eletivas, adicionar restrição para que as eletivas não sejam obrigatórias
            "PCB_Adriana Vivacqua/4.0",
            "PCB_Daniel Sadoc/4.0",
        ]

        self.assertEqual(result, expected_result)
        self.assertLessEqual(result_value, 0)


if __name__ == "__main__":
    unittest.main()
