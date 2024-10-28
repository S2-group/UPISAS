import unittest
from UPISAS.exceptions import DockerImageNotFoundOnDockerHub
from UPISAS.exemplar import Exemplar
from UPISAS.exemplars.demo_exemplar import DemoExemplar


class TestExemplar(unittest.TestCase):
    """
    Test cases for the Exemplar class using the DemoExemplar.
    """

    def setUp(self):
        self.exemplar = None

    def tearDown(self):
        if self.exemplar and self.exemplar.exemplar_container:
            self.exemplar.stop_container()

    def test_init_successfully_wihout_auto_start(self):
        self.exemplar = DemoExemplar(auto_start=False)
        self.assertEqual(self.exemplar.get_container_status(), "created")

    def test_init_successfully_with_auto_start(self):
        self.exemplar = DemoExemplar(auto_start=True)
        self.assertEqual(self.exemplar.get_container_status(), "running")

    def test_init_image_not_found_on_dockerhub(self):

        with self.assertRaises(DockerImageNotFoundOnDockerHub):
            class NonExistingExemplar(Exemplar):
                def __init__(self, auto_start=False, container_name="upisas-demo"):
                    docker_config = {"name": "upisas_test",
                                     "image": "very_strange_image_name_3456876",
                                     "ports": {3000: 3000}}
                    super().__init__("http://localhost:3000", docker_config, auto_start)
                def start_run(self, app):
                    None
            NonExistingExemplar(auto_start=False)

    def test_start_container_successfully(self):
        self.exemplar = DemoExemplar(auto_start=False)
        successful = self.exemplar.start_container()
        self.assertTrue(successful)
        self.assertEqual(self.exemplar.get_container_status(), "running")

    def test_stop_container_without_removing_successfully(self):
        self.exemplar = DemoExemplar(auto_start=True)
        successful = self.exemplar.stop_container(remove=False)
        self.assertTrue(successful)
        self.assertEqual(self.exemplar.get_container_status(), "exited")

    def test_stop_container_with_removing_successfully(self):
        self.exemplar = DemoExemplar(auto_start=True)
        successful = self.exemplar.stop_container(remove=True)
        self.assertTrue(successful)
        self.assertEqual(self.exemplar.get_container_status(), "removed")

    def test_pause_container_successfully(self):
        self.exemplar = DemoExemplar(auto_start=True)
        successful = self.exemplar.pause_container()
        self.assertTrue(successful)
        self.assertEqual(self.exemplar.get_container_status(), "paused")

    def test_pause_container_not_successfully(self):
        self.exemplar = DemoExemplar(auto_start=False)
        successful = self.exemplar.pause_container()
        self.assertFalse(successful)
        self.assertEqual(self.exemplar.get_container_status(), "created")

    def test_unpause_container_successfully(self):
        self.exemplar = DemoExemplar(auto_start=True)
        self.exemplar.pause_container()
        successful = self.exemplar.unpause_container()
        self.assertTrue(successful)
        self.assertEqual(self.exemplar.get_container_status(), "running")

    def test_unpause_container_not_successfully(self):
        self.exemplar = DemoExemplar(auto_start=False)
        successful = self.exemplar.unpause_container()
        self.assertFalse(successful)
        self.assertEqual(self.exemplar.get_container_status(), "created")


if __name__ == '__main__':
    unittest.main()
