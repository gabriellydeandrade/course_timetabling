from unittest import TestCase, main, skip
from unittest.mock import patch
import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # FIXME quero corrigir de outra forma

from main import init_model
from database.service_google_sheet import get_professors

import pandas as pd


@patch(
    "database.service_google_sheet.read_google_sheet_to_dataframe",
    return_value=pd.DataFrame(
        {
            "Alocar": ["TRUE", "TRUE", "TRUE"],
            "Nome curto": ["Adriana Vivacqua", "Daniel Sadoc", "Raphael Bernardino"],
            "Disciplinas aptas": ["ICP145,ICP616", "", ""],
            "Área de conhecimento": ["ED,ES,H", "ED,CD", ""],
            "Categoria": ["PP", "PP", "PS"],
        }
    ),
)
class TestProfessorsConstructionSet(TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def test_get_professors_from_google_sheets(self, mock_read_google_sheet):
        result_permanent, result_substitute = get_professors()

        expected_permanent = pd.DataFrame(
            {
                "qualified_courses": ["ICP145,ICP616", ""],
                "expertise": ["ED,ES,H", "ED,CD"],
                "category": ["PP", "PP"],
            },
            index=["Adriana Vivacqua", "Daniel Sadoc"]
        )
        expected_permanent.index.name = "professor"

        expected_substitute = pd.DataFrame(
            {
                "qualified_courses": [""],
                "expertise": [""],
                "category": ["PS"],
            },
            index=["Raphael Bernardino"]
        )
        expected_permanent.index.name = "professor"

        pd.testing.assert_frame_equal(result_permanent, expected_permanent)
        pd.testing.assert_frame_equal(result_substitute, expected_substitute)


@skip("implementar")
class TestCourseTimetabling(TestCase):

    def setUp(self) -> None:
        return super().setUp()

    @patch("input.professores", ["Prof1", "Prof2"])
    @patch("input.professores_permanentes", ["Prof1"])
    @patch("input.professores_substitutos", ["Prof2"])
    @patch(
        "input.disciplinas",
        {
            "ICP131_A": ["ICP131", [("SEG", "8:00-10:00"), ("QUA", "8:00-10:00")], 4],
            "ICP370": ["ICP370", [("QUA", "8:00-10:00"), ("SEX", "8:00-10:00")], 4],
        },
    )
    @patch(
        "utils.get_disciplinas_dias_horarios",
        return_value=(
            ["SEG", "QUA", "SEX"],
            ["8:00-10:00", "8:00-10:00", "8:00-10:00"],
        ),
    )
    @patch(
        "utils.professor_apto",
        side_effect=lambda p: ["ICP131_A"] if p == "Prof1" else [],
    )
    @patch("utils.get_carga_horaria", side_effect=lambda D, d: D[d][1][0])
    @patch(
        "utils.get_disciplinas_a_partir_de_um_dia",
        side_effect=lambda D, dia: set(D.keys()),
    )
    @patch(
        "utils.get_disciplinas_a_partir_de_um_horario",
        side_effect=lambda D, horario: set(D.keys()),
    )
    @patch("utils.get_codigo_disciplinas", return_value=set(["ICP131_A", "ICP370"]))
    def test_model(
        self,
        mock_get_disciplinas_dias_horarios,
        mock_professor_apto,
        mock_get_carga_horaria,
        mock_get_disciplinas_a_partir_de_um_dia,
        mock_get_disciplinas_a_partir_de_um_horario,
        mock_get_codigo_disciplinas,
    ):
        professor_timeschedule, model_value = init_model()

        expected_schedule = [
            "Prof1_ICP131_A_SEG_8:00-10:00 1.0",
            "Prof1_ICP131_A_QUA_8:00-10:00 1.0",
        ]

        self.assertEqual(professor_timeschedule, expected_schedule)
        self.assertAlmostEqual(model_value, 2.0, places=1)

    def test_main(self):
        # init_model()
        self.assertEqual(1, 1)


if __name__ == "__main__":
    main()