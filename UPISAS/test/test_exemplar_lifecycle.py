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
        if self.proc is not None:
            self.proc.kill()
            self.proc.wait()
        self.exemplar.stop()

    def test_start(self):
        self.exemplar.start()
        # time.sleep(1)
        _, container_status = self.exemplar.get_container()
        self.assertEqual(container_status, "running")

    def test_stop(self):
        self.exemplar.start()
        self.exemplar.stop()
        _, container_status = self.exemplar.get_container()
        self.assertEqual(container_status, "exited")

    def test_pause(self):
        self.exemplar.start()
        self.exemplar.pause()
        _, container_status = self.exemplar.get_container()
        self.assertEqual(container_status, "paused")

    def test_unpause(self):
        self.exemplar.start()
        self.exemplar.pause()
        self.exemplar.unpause()
        _, container_status = self.exemplar.get_container()
        self.assertEqual(container_status, "running")


if __name__ == '__main__':
    unittest.main()
