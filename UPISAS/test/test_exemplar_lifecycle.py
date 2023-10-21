import unittest
from UPISAS.exemplar import Exemplar
import time
from UPISAS.test import create_server_process


class TestExemplarLifecyle(unittest.TestCase):
    """
    Test cases for the Exemplar class, lifecycle methods (start, stop, pause, unpause)
    Run by `python -m UPISAS.test.test_exemplar_lifecycle` on the parent folder.
    """
    def setUp(self):
        self.proc = create_server_process('UPISAS/test/http-test-server/app.js')
        time.sleep(1)
        self.exemplar = Exemplar("http://localhost:3000", "gabrielmoreno/swim", "swim", auto_start=False)

    def tearDown(self):
        self.exemplar.stop()
        self.proc.kill()
        self.proc.wait()

    def test_create_successfully(self):
        self.assertEqual(self.exemplar.get_container_status(), "created")

    def test_start_successfully(self):
        successful = self.exemplar.start()
        self.assertTrue(successful)
        
        self.assertEqual(self.exemplar.get_container_status(), "running")

    def test_stop_successfully(self):
        self.exemplar.start()
        successful = self.exemplar.stop(remove=False)
        self.assertTrue(successful)
        self.assertEqual(self.exemplar.get_container_status(), "exited")

    def test_pause_successfully(self):
        self.exemplar.start()
        successful = self.exemplar.pause()
        self.assertTrue(successful)
        self.assertEqual(self.exemplar.get_container_status(), "paused")

    def test_pause_not_successfully(self):
        successful = self.exemplar.pause()
        self.assertFalse(successful)
        self.assertEqual(self.exemplar.get_container_status(), "created")

    def test_unpause_successfully(self):
        self.exemplar.start()
        self.exemplar.pause()
        successful = self.exemplar.unpause()
        self.assertTrue(successful)
        self.assertEqual(self.exemplar.get_container_status(), "running")

    def test_unpause_not_successfully(self):
        successful = self.exemplar.unpause()
        self.assertFalse(successful)
        self.assertEqual(self.exemplar.get_container_status(), "created")


if __name__ == '__main__':
    unittest.main()
