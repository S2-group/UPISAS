import unittest
from UPISAS.exemplar import Exemplar
from subprocess import Popen
import time


class TestExemplarInit(unittest.TestCase):
    """
    Test cases for the Exemplar class, __init__ method
    Run by `python -m UPISAS.test.test_exemplar_init` on the parent folder.
    """
    def setUp(self):
        self.proc = None

    def tearDown(self):
        if self.proc is not None:
            self.proc.kill()
            self.proc.wait()

    def test_init_successfully(self):
        self.proc = Popen(['node', 'UPISAS/test/http-test-server/app.js', '-d'])
        time.sleep(1)
        exemplar = Exemplar("http://localhost:3000", "gabrielmoreno/swim", "swim", auto_start=False)
        self.assertIsNotNone(exemplar.monitor_schema)
        self.assertIsNotNone(exemplar.potential_adaptations_schema_all)
        self.assertIsNotNone(exemplar.potential_adaptations_schema_single)
        self.assertIsNotNone(exemplar.potential_adaptations_values)
        exemplar.stop()

    def test_init_server_not_up(self):
        with self.assertRaises(SystemExit) as cm:
            Exemplar("http://localhost:3000", "gabrielmoreno/swim", "swim", auto_start=False)
        self.assertEqual(cm.exception.code, 1)

    def test_init_endpoint_adaptations_not_present(self):
        with self.assertRaises(SystemExit) as cm:
            self.proc = Popen(['node', 'UPISAS/test/http-test-server/app-no-endpoints.js', '-d'])
            time.sleep(1)
            Exemplar("http://localhost:3000", "gabrielmoreno/swim", "swim", auto_start=False)
        print("test_init_endpoint_not_existing: " + str(cm.exception.code))
        self.assertEqual(cm.exception.code, 2)

    def test_init_endpoint_monitor_schema_not_present(self):
        with self.assertRaises(SystemExit) as cm:
            self.proc = Popen(['node', 'UPISAS/test/http-test-server/app-only-adaptations-endpoint.js', '-d'])
            time.sleep(1)
            Exemplar("http://localhost:3000", "gabrielmoreno/swim", "swim", auto_start=False)
        self.assertEqual(cm.exception.code, 3)


if __name__ == '__main__':
    unittest.main()
