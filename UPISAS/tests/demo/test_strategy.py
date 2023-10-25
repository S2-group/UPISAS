import unittest
import time

from UPISAS import perform_get_request, ServerNotReachable
from UPISAS.exceptions import EndpointNotReachable
from UPISAS.exemplars.demo_exemplar import DemoExemplar
from UPISAS.strategies.demo_strategy import DemoStrategy


class TestStrategy(unittest.TestCase):
    """
    Test cases for the Strategy class, using the DemoStrategy.
    Run by `python -m UPISAS.tests.demo.test_strategy` on the parent folder.
    """

    def setUp(self):
        self.exemplar = DemoExemplar(auto_start=True)

    def tearDown(self):
        if self.exemplar and self.exemplar.exemplar_container:
            self.exemplar.stop_container()

    def test_get_adaptation_options_successfully(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.strategy.get_adaptation_options_schema()
        with self.assertLogs() as cm:
            self.strategy.get_adaptation_options()
            self.assertTrue("JSON Schema validated" in ", ".join(cm.output))
        self.assertIsNotNone(self.strategy.knowledge.adaptation_options)

    def test_monitor_successfully(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.strategy.get_monitor_schema()
        with self.assertLogs() as cm:
            successful = self.strategy.monitor()
            self.assertTrue("JSON Schema validated" in ", ".join(cm.output))
        self.assertTrue(successful)
        self.assertNotEqual(self.strategy.knowledge.monitored_data, dict())

    def test_execute_successfully(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.strategy.get_execute_schema()
        with self.assertLogs() as cm:
            successful = self.strategy.execute({"x": 2, "y": 5})
            self.assertTrue("JSON Schema validated" in ", ".join(cm.output))
        self.assertTrue(successful)

    def test_analyze_successfully(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.strategy.monitor()
        successful = self.strategy.analyze()
        self.assertTrue(successful)
        self.assertNotEqual(self.strategy.knowledge.analysis_data, dict())

    def test_plan_successfully(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.strategy.monitor()
        self.strategy.analyze()
        successful = self.strategy.plan()
        self.assertTrue(successful)
        self.assertNotEqual(self.strategy.knowledge.plan_data, dict())

    def test_adaptation_options_schema_endpoint_reachable(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.strategy.get_adaptation_options_schema()
        self.assertIsNotNone(self.strategy.knowledge.adaptation_options_schema)

    def test_monitor_schema_endpoint_reachable(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.strategy.get_monitor_schema()
        self.assertIsNotNone(self.strategy.knowledge.monitor_schema)

    def test_execute_schema_endpoint_reachable(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.strategy.get_execute_schema()
        self.assertIsNotNone(self.strategy.knowledge.execute_schema)

    def test_server_not_reachable(self):
        self.strategy = DemoStrategy(self.exemplar)
        with self.assertRaises(ServerNotReachable):
            self.strategy.ping()

    def test_adaptation_options_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        self.strategy = DemoStrategy(self.exemplar)
        with self.assertRaises(EndpointNotReachable):
            self.strategy.get_adaptation_options()

    def test_monitor_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        self.strategy = DemoStrategy(self.exemplar)
        successful = self.strategy.monitor()
        self.assertFalse(successful)
        self.assertDictEqual(self.strategy.knowledge.monitored_data, dict())

    def test_execute_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        self.strategy = DemoStrategy(self.exemplar)
        successful = self.strategy.execute({"x": 2, "y": 5})
        self.assertFalse(successful)

    def test_adaptation_options_schema_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        self.strategy = DemoStrategy(self.exemplar)
        with self.assertRaises(EndpointNotReachable):
            self.strategy.get_adaptation_options_schema()

    def test_monitor_schema_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        self.strategy = DemoStrategy(self.exemplar)
        with self.assertRaises(EndpointNotReachable):
            self.strategy.get_monitor_schema()

    def test_execute_schema_endpoint_not_reachable(self):
        self._start_server_and_wait_until_is_up(app="app-no-endpoints.js")
        self.strategy = DemoStrategy(self.exemplar)
        with self.assertRaises(EndpointNotReachable):
            self.strategy.get_execute_schema()

    def test_json_validation_no_schema_present(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        with self.assertLogs() as cm:
            self.strategy.monitor()
            self.assertTrue("No complete JSON Schema provided for validation" in ", ".join(cm.output))

    def test_json_validation_no_complete_schema_present(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.strategy.get_monitor_schema()
        self.strategy.knowledge.monitor_schema = {
            "type": "object",
            "properties": {
            }
        }
        with self.assertLogs() as cm:
            self.strategy.monitor()
            self.assertTrue("No complete JSON Schema provided for validation" in ", ".join(cm.output))

    def test_json_validation_json_schema_invalid(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.strategy.get_monitor_schema()
        self.strategy.knowledge.monitor_schema = {
            "type": "strange_value",
            "properties": {
                "f": {
                    "type": "number",
                }
            }
        }
        with self.assertLogs() as cm:
            self.strategy.monitor()
            self.assertTrue("SchemaError" in ", ".join(cm.output))

    def test_json_validation_json_instance_not_conforming_to_schema(self):
        self._start_server_and_wait_until_is_up()
        self.strategy = DemoStrategy(self.exemplar)
        self.strategy.get_monitor_schema()
        self.strategy.knowledge.monitor_schema = {
            "type": "object",
            "properties": {
                "f": {
                    "type": "string",
                }
            }
        }
        with self.assertLogs() as cm:
            self.strategy.monitor()
            self.assertTrue("ValidationError" in ", ".join(cm.output))

    def _start_server_and_wait_until_is_up(self, base_endpoint="http://localhost:3000", app="app.js"):
        self.exemplar.start_run(app)
        while True:
            time.sleep(1)
            print("trying to connect...")
            _, status_code = perform_get_request(base_endpoint)
            print(status_code)
            if status_code < 400:
                return


if __name__ == '__main__':
    unittest.main()
