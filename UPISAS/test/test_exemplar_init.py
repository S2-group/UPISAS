import unittest
from UPISAS.test import create_server_process
from UPISAS.exemplar import Exemplar
import docker

class TestExemplarInit(unittest.TestCase):
    """
    Test cases for the Exemplar class, __init__ method
    Run by `python -m UPISAS.test.test_exemplar_init` on the parent folder.
    """

    incomplete_constructor = False
    swim_docker_kwargs = {"ports" : {5901: 5901, 6901: 6901}}
    def setUp(self):
        self.proc = None

    def tearDown(self):
        if self.proc is not None:
            self.proc.kill()
            self.proc.wait()
        if self.incomplete_constructor == True:
            docker_client = docker.from_env()
            docker_client.api.remove_container("swim")

    def test_init_successfully(self):
        self.incomplete_constructor = False
        self.proc = create_server_process('UPISAS/test/http-test-server/app.js')
        
        exemplar = Exemplar("http://localhost:3000", "gabrielmoreno/swim", "swim", self.swim_docker_kwargs, auto_start=True)
        self.assertIsNotNone(exemplar.monitor_schema)
        self.assertIsNotNone(exemplar.potential_adaptations_schema_all)
        self.assertIsNotNone(exemplar.potential_adaptations_schema_single)
        self.assertIsNotNone(exemplar.potential_adaptations_values)
        exemplar.stop()

    def test_init_server_not_up(self):
        self.incomplete_constructor = True
        with self.assertRaises(SystemExit) as cm:
            Exemplar("http://localhost:3000", "gabrielmoreno/swim", "swim", self.swim_docker_kwargs, auto_start=False)
        self.assertEqual(cm.exception.code, 1)


    def test_init_endpoint_adaptations_not_present(self):
        self.incomplete_constructor = True
        with self.assertRaises(SystemExit) as cm:
            self.proc = create_server_process('UPISAS/test/http-test-server/app-no-endpoints.js')
            Exemplar("http://localhost:3000", "gabrielmoreno/swim", "swim", self.swim_docker_kwargs, auto_start=False)
        print("test_init_endpoint_not_existing: " + str(cm.exception.code))
        self.assertEqual(cm.exception.code, 2)
        

    def test_init_endpoint_monitor_schema_not_present(self):
        self.incomplete_constructor = True
        with self.assertRaises(SystemExit) as cm:
            self.proc = create_server_process('UPISAS/test/http-test-server/app-only-adaptations-endpoint.js')
            Exemplar("http://localhost:3000", "gabrielmoreno/swim", "swim", self.swim_docker_kwargs, auto_start=False)
        self.assertEqual(cm.exception.code, 3)
        

if __name__ == '__main__':
    unittest.main()
