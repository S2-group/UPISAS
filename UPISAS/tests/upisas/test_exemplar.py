import unittest
import jsonschema
import time

from UPISAS import get_response_for_get_request
from UPISAS.exceptions import DockerImageNotFoundOnDockerHub, EndpointNotReachable, IncompleteJSONSchema
from UPISAS.exemplar import Exemplar
from UPISAS.exemplars.demo_exemplar import DemoExemplar

from UPISAS import ServerNotReachable


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
        class FailingExemplar(Exemplar):
            def __init__(self, auto_start=False):
                docker_config = {"name": "upisas_test",
                                 "image": "very_strange_image_name_3456876",
                                 "ports": {3000: 3000}}
                super().__init__("http://localhost:3000", docker_config, auto_start)

            def start_run(self):
                self.exemplar_container.exec_run(cmd = f' sh -c "cd /usr/src/app && node app-no-endpoints.js" ', detach=True)


        with self.assertRaises(DockerImageNotFoundOnDockerHub):
            FailingExemplar(auto_start=False)

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


class TestDemoExemplar(unittest.TestCase):

    def setUp(self):
        self.exemplar = DemoExemplar(auto_start=True)

    def tearDown(self):
        if self.exemplar and self.exemplar.exemplar_container:
            self.exemplar.stop_container()

    def test_get_adaptation_options_successfully(self):
        self._start_server_and_wait_until_is_up()
        self.exemplar.get_adaptation_options_schema()
        with self.assertLogs() as cm:
            self.exemplar.get_adaptation_options()
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertIsNotNone(self.exemplar.knowledge.adaptation_options)

    def test_monitor_successfully(self):
        self._start_server_and_wait_until_is_up()
        self.exemplar.get_monitor_schema()
        with self.assertLogs() as cm:
            successful = self.exemplar.monitor()
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertTrue(successful)
        self.assertNotEqual(self.exemplar.knowledge.monitored_data, dict())

    def test_execute_successfully(self):
        self._start_server_and_wait_until_is_up()
        self.exemplar.get_execute_schema()
        with self.assertLogs() as cm:
            successful = self.exemplar.execute({"x": 2.1, "y": 5.3})
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertTrue(successful)

    def test_adaptation_options_schema_endpoint_reachable(self):
        self._start_server_and_wait_until_is_up()
        self.exemplar.get_adaptation_options_schema()
        self.assertIsNotNone(self.exemplar.knowledge.adaptation_options_schema)

    def test_monitor_schema_endpoint_reachable(self):
        self._start_server_and_wait_until_is_up()
        self.exemplar.get_monitor_schema()
        self.assertIsNotNone(self.exemplar.knowledge.monitor_schema)

    def test_execute_schema_endpoint_reachable(self):
        self._start_server_and_wait_until_is_up()
        self.exemplar.get_execute_schema()
        self.assertIsNotNone(self.exemplar.knowledge.execute_schema)

    def test_server_not_reachable(self):
        with self.assertRaises(ServerNotReachable):
            self.exemplar.ping()

    def test_adaptation_options_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        with self.assertRaises(EndpointNotReachable):
            self.exemplar.get_adaptation_options()

    def test_monitor_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        with self.assertRaises(EndpointNotReachable):
            self.exemplar.monitor(with_validation=False)
        self.assertDictEqual(self.exemplar.knowledge.monitored_data, dict())

    def test_execute_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        with self.assertRaises(EndpointNotReachable):
            self.exemplar.execute({"x": 2.1, "y": 5.3}, with_validation=False)

    def test_adaptation_options_schema_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        with self.assertRaises(EndpointNotReachable):
            self.exemplar.get_adaptation_options_schema()

    def test_monitor_schema_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        with self.assertRaises(EndpointNotReachable):
            self.exemplar.get_monitor_schema()

    def test_execute_schema_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        with self.assertRaises(EndpointNotReachable):
            self.exemplar.get_execute_schema()

    def test_json_validation_no_schema_present(self):
        self._start_server_and_wait_until_is_up()
        with self.assertRaises(IncompleteJSONSchema):
            self.exemplar.monitor()

    def test_json_validation_no_complete_schema_present(self):
        self._start_server_and_wait_until_is_up()
        self.exemplar.get_monitor_schema()
        self.exemplar.knowledge.monitor_schema = {
            "type": "object",
            "properties": {
            }
        }
        with self.assertRaises(IncompleteJSONSchema):
            self.exemplar.monitor()

    def test_json_validation_json_schema_invalid(self):
        self._start_server_and_wait_until_is_up()
        self.exemplar.get_monitor_schema()
        self.exemplar.knowledge.monitor_schema = {
            "type": "strange_value",
            "properties": {
                "f": {
                    "type": "number",
                }
            }
        }
        with self.assertRaises(jsonschema.exceptions.SchemaError):
            self.exemplar.monitor()

    def test_json_validation_json_instance_not_conforming_to_schema(self):
        self._start_server_and_wait_until_is_up()
        self.exemplar.get_monitor_schema()
        self.exemplar.knowledge.monitor_schema = {
            "type": "object",
            "properties": {
                "f": {
                    "type": "string",
                }
            }
        }
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            self.exemplar.monitor()

    def _start_server_and_wait_until_is_up(self, base_endpoint="http://localhost:3000", app="app.js"):
        self.exemplar.start_run(app)
        while True:
            time.sleep(1)
            print("trying to connect...")
            response = get_response_for_get_request(base_endpoint)
            print(response.status_code)
            if response.status_code < 400:
                return


if __name__ == '__main__':
    unittest.main()
