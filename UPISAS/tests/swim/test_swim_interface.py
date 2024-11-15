import unittest
import time

from UPISAS import get_response_for_get_request, validate_schema
from UPISAS.exemplars.swim import SWIM
from UPISAS.strategies.empty_strategy import EmptyStrategy


class TestStrategy(unittest.TestCase):
    """
    Test cases for the Strategy class, using the DemoStrategy.
    Run by `python -m UPISAS.tests.demo.test_strategy` on the parent folder.
    """

    def setUp(self):
        self.exemplar = SWIM(auto_start=True)
        self._start_server_and_wait_until_is_up()
        self.strategy = EmptyStrategy(self.exemplar)

    def tearDown(self):
        if self.exemplar and self.exemplar.exemplar_container:
            self.exemplar.stop_container()

    def test_get_adaptation_options_successfully(self):
        self.exemplar.get_adaptation_options(with_validation=False)
        self.assertIsNotNone(self.exemplar.knowledge.adaptation_options)

    def test_monitor_successfully(self):
        successful = self.strategy.monitor(with_validation=False)
        self.assertTrue(successful)
        self.assertNotEqual(self.exemplar.knowledge.monitored_data, dict())

    def test_execute_successfully(self):
        successful = self.exemplar.execute({"server_number": 2, "dimmer_factor": 0.5}, with_validation=False)
        self.assertTrue(successful)

    def test_adaptation_options_schema_endpoint_reachable(self):
        self.exemplar.get_adaptation_options_schema()
        self.assertIsNotNone(self.exemplar.knowledge.adaptation_options_schema)

    def test_monitor_schema_endpoint_reachable(self):
        self.exemplar.get_monitor_schema()
        self.assertIsNotNone(self.exemplar.knowledge.monitor_schema)

    def test_execute_schema_endpoint_reachable(self):
        self.exemplar.get_execute_schema()
        self.assertIsNotNone(self.exemplar.knowledge.execute_schema)

    def test_schema_of_adaptation_options(self):
        self.exemplar.get_adaptation_options_schema()
        with self.assertLogs() as cm:
            self.exemplar.get_adaptation_options()
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertIsNotNone(self.exemplar.knowledge.adaptation_options)

    def test_schema_of_monitor(self):
        self.exemplar.get_monitor_schema()
        with self.assertLogs() as cm:
            successful = self.exemplar.monitor()
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertTrue(successful)
        self.assertNotEqual(self.exemplar.knowledge.monitored_data, dict())

    def test_schema_of_execute(self):
        self.exemplar.get_execute_schema()
        with self.assertLogs() as cm:
            successful = self.exemplar.execute({"server_number": 2, "dimmer_factor": 0.5})
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertTrue(successful)

    def _start_server_and_wait_until_is_up(self, base_endpoint="http://localhost:3000"):
        self.exemplar.start_run()
        while True:
            time.sleep(1)
            print("trying to connect...")
            response = get_response_for_get_request(base_endpoint)
            print(response.status_code)
            if response.status_code < 400:
                return


if __name__ == '__main__':
    unittest.main()
