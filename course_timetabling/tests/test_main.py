import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.utils import get_course_schedule
from main import CourseTimetabling

class TestInitializeVariablesAndCoefficients(unittest.TestCase):

    @patch("utils.utils.get_qualified_courses_for_professor")
    @patch("utils.utils.get_course_schedule")
    def setUp(self, mock_get_schedule, mock_get_qualified) -> None:
        self.PROFESSORS = ["Prof1", "Prof2"]
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
                "course_type": "SVC",
            },
        }
        mock_get_qualified.return_value = ["OBG-BCC1-1"]
        mock_get_schedule.side_effect = lambda courses, course: ("SEG", "13:00-15:00") if course == "OBG-BCC1-1" else ("TER", "15:00-17:00")

        self.timetabling = CourseTimetabling(self.PROFESSORS, ["Prof1"], ["Prof2"], self.COURSES, {}, [], [])
        self.timetabling.initialize_variables_and_coefficients()
        return super().setUp()
    
    def test_set_coefficient_to_one_if_professor_is_qualified_for_class(self):
        
        self.assertIn("Prof1", self.timetabling.coefficients)
        self.assertIn("OBG-BCC1-1", self.timetabling.coefficients["Prof1"])

        for day, value in self.timetabling.coefficients["Prof1"]["OBG-BCC1-1"].items():
            time = list(value.keys())[0]
            self.assertEqual(self.timetabling.coefficients["Prof1"]["OBG-BCC1-1"][day][time], 1)

        self.assertIn("OBG-BCC1-1", self.timetabling.variables["Prof1"])

    def test_set_coefficient_to_zero_if_professor_is_not_qualified_for_class(self):
        
        self.assertIn("Prof1", self.timetabling.coefficients)
        self.assertIn("OBG-BCC1-2", self.timetabling.coefficients["Prof1"])

        for day, value in self.timetabling.coefficients["Prof1"]["OBG-BCC1-2"].items():
            time = list(value.keys())[0]
            self.assertEqual(self.timetabling.coefficients["Prof1"]["OBG-BCC1-2"][day][time], 0)

        self.assertIn("OBG-BCC1-2", self.timetabling.variables["Prof1"])

# class TestCourseTimetabling(unittest.TestCase):

    # def test_add_credit_slack_variables(self):
    #     timetabling = CourseTimetabling(["Prof1"], ["Prof1"], [], {}, {}, [], [])
    #     timetabling.add_credit_slack_variables()

    #     # Assertions
    #     self.assertIn("Prof1", timetabling.slack_variables)

    # @patch("utils.utils.get_course_schedule")
    # def test_add_constraints(self, mock_get_schedule):
    #     PROFESSORS = ["Prof1", "Prof2"]
    #     PERMANENT_PROFESSORS = ["Prof1"]
    #     COURSES = {
    #         "OBG-BCC1-1": {
    #             "course_id": "ICP131",
    #             "credits": 4,
    #             "day": "SEG,QUA",
    #             "time": "13:00-15:00,08:00-10:00",
    #             "course_type": "OBG",
    #         },
    #         "OBG-BCC1-2": {
    #             "course_id": "ICP123",
    #             "credits": 4,
    #             "day": "TER,QUI",
    #             "time": "15:00-17:00",
    #             "course_type": "SVC",
    #         },
    #     }

    #     timetabling = CourseTimetabling(PROFESSORS, PERMANENT_PROFESSORS, ["Prof2"], COURSES, {}, ["SEG", "TER"], ["13:00-15:00", "15:00-17:00"])
    #     timetabling.initialize_variables_and_coefficients()
    #     timetabling.add_credit_slack_variables()

    #     mock_get_schedule.side_effect = lambda courses, course: ("SEG", "13:00-15:00") if course == "OBG-BCC1-1" else ("TER", "15:00-17:00")

    #     timetabling.add_constraints()

    #     # Assertions
    #     for professor in PROFESSORS:
    #         for course in COURSES.keys():
    #             day, time = get_course_schedule(COURSES, course)
    #             self.assertIn(course, timetabling.variables[professor])
    #             self.assertIn(day, timetabling.variables[professor][course])
    #             self.assertIn(time, timetabling.variables[professor][course][day])

    # @patch("utils.utils.get_course_schedule")
    # def test_set_objective(self, mock_get_schedule):
    #     PROFESSORS = ["Prof1", "Prof2"]
    #     PERMANENT_PROFESSORS = ["Prof1"]
    #     COURSES = {
    #         "OBG-BCC1-1": {
    #             "course_id": "ICP131",
    #             "credits": 4,
    #             "day": "SEG,QUA",
    #             "time": "13:00-15:00,08:00-10:00",
    #             "course_type": "OBG",
    #         },
    #         "OBG-BCC1-2": {
    #             "course_id": "ICP123",
    #             "credits": 4,
    #             "day": "TER,QUI",
    #             "time": "15:00-17:00",
    #             "course_type": "SVC",
    #         },
    #     }

    #     timetabling = CourseTimetabling(PROFESSORS, PERMANENT_PROFESSORS, ["Prof2"], COURSES, {}, ["SEG", "TER"], ["13:00-15:00", "15:00-17:00"])
    #     timetabling.initialize_variables_and_coefficients()
    #     timetabling.add_credit_slack_variables()

    #     mock_get_schedule.side_effect = lambda courses, course: ("SEG", "13:00-15:00") if course == "OBG-BCC1-1" else ("TER", "15:00-17:00")

    #     timetabling.set_objective()

    #     # Assertions
    #     self.assertIsNotNone(timetabling.model.getObjective())

if __name__ == "__main__":
    unittest.main()