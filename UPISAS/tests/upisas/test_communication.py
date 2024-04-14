import unittest
import time

import jsonschema

from UPISAS import get_response_for_get_request, ServerNotReachable
from UPISAS.exceptions import EndpointNotReachable, IncompleteJSONSchema
from UPISAS.exemplars.demo_exemplar import DemoExemplar
from UPISAS.strategies.demo_strategy import DemoStrategy


class TestStrategy(unittest.TestCase):
    """
    Test cases for the Strategy class, using the DemoStrategy.
    """

    def setUp(self):
        self.exemplar = DemoExemplar(auto_start=True)

    def tearDown(self):
        if self.exemplar and self.exemplar.exemplar_container:
            self.exemplar.stop_container()

    def test_get_adaptation_options_successfully(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.exemplar.get_adaptation_options_schema()
        with self.assertLogs() as cm:
            self.exemplar.get_adaptation_options()
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertIsNotNone(self.exemplar.knowledge.adaptation_options)

    def test_monitor_successfully(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.exemplar.get_monitor_schema()
        with self.assertLogs() as cm:
            successful = self.exemplar.monitor()
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertTrue(successful)
        self.assertNotEqual(self.exemplar.knowledge.monitored_data, dict())

    def test_execute_successfully(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.exemplar.get_execute_schema()
        with self.assertLogs() as cm:
            successful = self.exemplar.execute({"x": 2.1, "y": 5.3})
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertTrue(successful)

    def test_adaptation_options_schema_endpoint_reachable(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.exemplar.get_adaptation_options_schema()
        self.assertIsNotNone(self.exemplar.knowledge.adaptation_options_schema)

    def test_monitor_schema_endpoint_reachable(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.exemplar.get_monitor_schema()
        self.assertIsNotNone(self.exemplar.knowledge.monitor_schema)

    def test_execute_schema_endpoint_reachable(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.exemplar.get_execute_schema()
        self.assertIsNotNone(self.exemplar.knowledge.execute_schema)

    def test_analyze_successfully(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.exemplar.get_monitor_schema()
        self.exemplar.monitor()
        successful = self.strategy.analyze()
        self.assertTrue(successful)
        self.assertNotEqual(self.exemplar.knowledge.analysis_data, dict())

    def test_plan_successfully(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.exemplar.get_monitor_schema()
        self.exemplar.monitor()
        self.strategy.analyze()
        successful = self.strategy.plan()
        self.assertTrue(successful)
        self.assertNotEqual(self.exemplar.knowledge.plan_data, dict())

    def test_server_not_reachable(self):
        self.strategy = DemoStrategy(self.exemplar)
        with self.assertRaises(ServerNotReachable):
            self.strategy.ping()

    def test_adaptation_options_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        self.strategy = DemoStrategy(self.exemplar)
        with self.assertRaises(EndpointNotReachable):
            self.exemplar.get_adaptation_options()

    def test_monitor_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        self.strategy = DemoStrategy(self.exemplar)
        with self.assertRaises(EndpointNotReachable):
            self.exemplar.monitor(with_validation=False)
        self.assertDictEqual(self.exemplar.knowledge.monitored_data, dict())

    def test_execute_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        self.strategy = DemoStrategy(self.exemplar)
        with self.assertRaises(EndpointNotReachable):
            self.exemplar.execute({"x": 2.1, "y": 5.3}, with_validation=False)

    def test_adaptation_options_schema_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        self.strategy = DemoStrategy(self.exemplar)
        with self.assertRaises(EndpointNotReachable):
            self.exemplar.get_adaptation_options_schema()

    def test_monitor_schema_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        self.strategy = DemoStrategy(self.exemplar)
        with self.assertRaises(EndpointNotReachable):
            self.exemplar.get_monitor_schema()

    def test_execute_schema_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        self.strategy = DemoStrategy(self.exemplar)
        with self.assertRaises(EndpointNotReachable):
            self.exemplar.get_execute_schema()

    def test_json_validation_no_schema_present(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        with self.assertRaises(IncompleteJSONSchema):
            self.exemplar.monitor()

    def test_json_validation_no_complete_schema_present(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
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
        self.strategy = DemoStrategy(self.exemplar)
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
        self.strategy = DemoStrategy(self.exemplar)
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
