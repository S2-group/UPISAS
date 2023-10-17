import unittest
from UPISAS.exemplar import Exemplar
from subprocess import Popen
import time


class TestExemplarLifecyle(unittest.TestCase):
    """
    Test cases for the Exemplar class, lifecycle methods (start, stop, pause, unpause)
    Run by `python -m UPISAS.test.test_exemplar_lifecycle` on the parent folder.
    """
    def setUp(self):
        self.proc = Popen(['node', 'UPISAS/test/http-test-server/app.js', '-d'])
        time.sleep(1)
        self.exemplar = Exemplar("http://localhost:3000", "gabrielmoreno/swim", "swim", auto_start=False)
        # this is just to make sure that the container is not running (e.g. from a previous test execution)
        self.exemplar.stop()
        container, container_status = self.exemplar.get_container()
        self.assertEqual(container_status, "exited")

    def tearDown(self):
        self.exemplar.stop()
        self.proc.kill()
        self.proc.wait()

    def test_start_successfully(self):
        successful = self.exemplar.start()
        self.assertTrue(successful)
        _, container_status = self.exemplar.get_container()
        self.assertEqual(container_status, "running")

    def test_stop_successfully(self):
        self.exemplar.start()
        successful = self.exemplar.stop()
        self.assertTrue(successful)
        _, container_status = self.exemplar.get_container()
        self.assertEqual(container_status, "exited")

    def test_pause_successfully(self):
        self.exemplar.start()
        successful = self.exemplar.pause()
        self.assertTrue(successful)
        _, container_status = self.exemplar.get_container()
        self.assertEqual(container_status, "paused")

    def test_pause_not_successfully(self):
        successful = self.exemplar.pause()
        self.assertFalse(successful)
        _, container_status = self.exemplar.get_container()
        self.assertEqual(container_status, "exited")

    def test_unpause_successfully(self):
        self.exemplar.start()
        self.exemplar.pause()
        successful = self.exemplar.unpause()
        self.assertTrue(successful)
        _, container_status = self.exemplar.get_container()
        self.assertEqual(container_status, "running")

    def test_unpause_not_successfully(self):
        successful = self.exemplar.unpause()
        self.assertFalse(successful)
        _, container_status = self.exemplar.get_container()
        self.assertEqual(container_status, "exited")


if __name__ == '__main__':
    unittest.main()
