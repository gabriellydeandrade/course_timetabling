import unittest
from unittest.mock import patch, MagicMock
import gurobipy as gp
from gurobipy import GRB
from course_timetabling.utils.utils import get_disciplinas_dias_horarios, professor_apto, get_carga_horaria, get_disciplinas_a_partir_de_um_dia, get_disciplinas_a_partir_de_um_horario, get_codigo_disciplinas
import input

class TestGetCargaHoraria(unittest.TestCase):

    # professor, disciplina, dia, horario

    def test_upper(self):

        disciplinas_mock = {
            "ICP131_A": ["ICP131", [('SEG', '8:00-10:00'), ('QUA', '8:00-10:00')], 4],
            "ICP370": ["ICP370", [('QUA', '8:00-10:00'), ('SEX', '8:00-10:00')], 4]
        }
        expected_result = [['SEG', 'QUA'], ['8:00-10:00', '8:00-10:00']]
        
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

            # Assuming the functions from utils and input are imported correctly

            class TestCourseTimetabling(unittest.TestCase):

                @patch('input.professores', ['Prof1', 'Prof2'])
                @patch('input.professores_permanentes', ['Prof1'])
                @patch('input.professores_substitutos', ['Prof2'])
                @patch('input.disciplinas', {
                    "ICP131_A": ["ICP131", [('SEG', '8:00-10:00'), ('QUA', '8:00-10:00')], 4],
                    "ICP370": ["ICP370", [('QUA', '8:00-10:00'), ('SEX', '8:00-10:00')], 4]
                })
                @patch('utils.get_disciplinas_dias_horarios', return_value=(['SEG', 'QUA', 'SEX'], ['8:00-10:00', '8:00-10:00', '8:00-10:00']))
                @patch('utils.professor_apto', side_effect=lambda p: ["ICP131_A"] if p == "Prof1" else [])
                @patch('utils.get_carga_horaria', side_effect=lambda D, d: D[d][1][0])
                @patch('utils.get_disciplinas_a_partir_de_um_dia', side_effect=lambda D, dia: set(D.keys()))
                @patch('utils.get_disciplinas_a_partir_de_um_horario', side_effect=lambda D, horario: set(D.keys()))
                @patch('utils.get_codigo_disciplinas', return_value=set(["ICP131_A", "ICP370"]))
                def test_model(self, mock_get_disciplinas_dias_horarios, mock_professor_apto, mock_get_carga_horaria, mock_get_disciplinas_a_partir_de_um_dia, mock_get_disciplinas_a_partir_de_um_horario, mock_get_codigo_disciplinas):
                    m = gp.Model("CourseTimetabling")

                    P = input.professores
                    PP = input.professores_permanentes
                    PS = input.professores_substitutos
                    D = input.disciplinas
                    DISCIPLINA_DIAS, DISCILINA_HORARIOS = get_disciplinas_dias_horarios(D)

                    f = {}  # Coeficientes
                    X = {}  # Variáveis

                    for p in P:
                        f[p] = {}
                        X[p] = {}
                        disciplinas_aptas = professor_apto(p)

                        for d in D.keys():
                            f[p][d] = {}
                            X[p][d] = {}

                            CH = get_carga_horaria(D, d)
                            f[p][d][CH[0]] = {}
                            f[p][d][CH[0]][CH[1]] = {}

                            if p == "DUMMY":
                                a = 0.0001
                            elif d in disciplinas_aptas:
                                a = 1
                            else:
                                a = 0

                            f[p][d][CH[0]][CH[1]] = a

                            X[p][d][CH[0]] = {}
                            X[p][d][CH[0]][CH[1]] = {}
                            X[p][d][CH[0]][CH[1]] = m.addVar(
                                vtype=GRB.BINARY, name=f"{p}_{d}_{CH[0]}_{CH[1]}"
                            )

                    PNC = {}
                    for p in PP:
                        PNC[p] = {}
                        PNC[p] = m.addVar(vtype=GRB.INTEGER, name=f"PNC_{p}")

                    Wf = 1000
                    FALpp = 8

                    for p in PP:
                        m.addConstr(
                            gp.quicksum(
                                [
                                    X[p][d][get_carga_horaria(D, d)[0]][get_carga_horaria(D, d)[1]]
                                    * D[d][2]
                                    for d in D.keys()
                                ]
                            )
                            == FALpp - PNC[p]
                        )

                    m.setObjective(
                        expr=gp.quicksum(
                            (X[p][d][CH[0]][CH[1]] * f[p][d][CH[0]][CH[1]])
                            for p in P
                            for d in D.keys()
                            for CH in [get_carga_horaria(D, d)]
                        )
                        - 
                        gp.quicksum(Wf * PNC[pp] for pp in PP),
                        sense=GRB.MAXIMIZE
                    )

                    FALps = 12
                    for p in PS:
                        m.addConstr(
                            gp.quicksum(
                                [
                                    X[p][d][get_carga_horaria(D, d)[0]][get_carga_horaria(D, d)[1]]
                                    * D[d][2]
                                    for d in D.keys()
                                ]
                            )
                            <= FALps
                        )

                    for d in D.keys():
                        CH = get_carga_horaria(D, d)
                        m.addConstr(gp.quicksum([X[p][d][CH[0]][CH[1]] for p in P]) == 1)

                    for p in P:
                        if p == "DUMMY":
                            continue

                        for i in range(len(DISCIPLINA_DIAS)):
                            A = get_disciplinas_a_partir_de_um_dia(D, DISCIPLINA_DIAS[i])
                            B = get_disciplinas_a_partir_de_um_horario(D, DISCILINA_HORARIOS[i])
                            C = A.intersection(B)

                            m.addConstr(
                                gp.quicksum(
                                    [
                                        X[p][d][get_carga_horaria(D, d)[0]][get_carga_horaria(D, d)[1]]
                                        for d in C
                                    ]
                                )
                                <= 1
                            )

                    for p in P:
                        todas_disciplinas = get_codigo_disciplinas(D)
                        disciplinas_aptas = professor_apto(p)

                        disciplinas_nao_aptas = todas_disciplinas.difference(disciplinas_aptas)

                        m.addConstr(
                            gp.quicksum(
                                [
                                    X[p][d][get_carga_horaria(D, d)[0]][get_carga_horaria(D, d)[1]]
                                    for d in disciplinas_nao_aptas
                                ]
                            )
                            == 0
                        )

                    m.update()
                    m.optimize()

                    for v in m.getVars():
                        if v.X > 0:
                            print("%s %g" % (v.VarName, v.X))

                    print("Obj: %g" % m.ObjVal)

            if __name__ == '__main__':
                unittest.main()

if __name__ == '__main__':
    unittest.main()