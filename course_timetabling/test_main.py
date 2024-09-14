import unittest

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

if __name__ == '__main__':
    unittest.main()