import unittest
from UPISAS.Exemplar import Exemplar
from subprocess import Popen
import time


class TestExemplar(unittest.TestCase):
    """
    Test cases for the Exemplar class.
    Run by `python -m UPISAS.test.TestExemplar` on the parent folder.
    """
    def test_init_successful(self):
        with Popen(['node', 'http-test-server/app.js', '-d']) as proc:
            time.sleep(1)
            exemplar = Exemplar("http://localhost:3000", "gabrielmoreno/swim", "swim", auto_start=False)
            proc.kill()
        self.assertIsNotNone(exemplar.monitor_schema)
        self.assertIsNotNone(exemplar.potential_adaptations_schema_all)
        self.assertIsNotNone(exemplar.potential_adaptations_schema_single)
        self.assertIsNotNone(exemplar.potential_adaptations_values)

    def test_init_raising_error1(self):
        with self.assertRaises(SystemExit) as cm:
            Exemplar("http://localhost:300", "gabrielmoreno/swim", "swim", auto_start=False)
        self.assertEqual(cm.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
