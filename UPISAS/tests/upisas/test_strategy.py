import unittest
import time

from UPISAS import get_response_for_get_request
from UPISAS.exemplars.demo_exemplar import DemoExemplar
from UPISAS.strategies.demo_strategy import DemoStrategy
from UPISAS.goal_managers.demo_manager import DemoGoalManagement


class TestStrategy(unittest.TestCase):
    """
    Test cases for the Strategy class, using the DemoStrategy.
    """

    def setUp(self):
        self.exemplar = DemoExemplar(auto_start=True)

    def tearDown(self):
        if self.exemplar and self.exemplar.exemplar_container:
            self.exemplar.stop_container()

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
        self.goal_manager = DemoGoalManagement(self.exemplar, {
            "adapt": {
                "strategies": [DemoStrategy(self.exemplar)],
            }
        })
        self.strategy = DemoStrategy(self.exemplar)
        self.exemplar.get_monitor_schema()
        self.exemplar.monitor()
        self.strategy.analyze()
        successful = self.strategy.plan()
        conflicts = self.exemplar.check_for_update_conflicts()
        self.goal_manager.resolve_conflicts(conflicts)
        self.assertTrue(successful)
        self.assertNotEqual(self.exemplar.knowledge.plan_data, dict())

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
