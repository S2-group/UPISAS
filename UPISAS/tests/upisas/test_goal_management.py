import unittest
import jsonschema
import time

from UPISAS import get_response_for_get_request

from UPISAS.exceptions import DockerImageNotFoundOnDockerHub

from UPISAS.goal_management import GoalManagement
from UPISAS.goal_managers.demo_manager import DemoGoalManagement

from UPISAS.exemplar import Exemplar
from UPISAS.exemplars.demo_exemplar import DemoExemplar

from UPISAS.strategy import Strategy
from UPISAS.strategies.demo_strategy import DemoStrategy

from UPISAS import ServerNotReachable
from UPISAS.exceptions import EndpointNotReachable, IncompleteJSONSchema

class FixedStrategy(Strategy):
    """
    A fixed strategy that always returns True in analyze and plan.
    """

    def __init__(self, exemplar):
        super().__init__(exemplar)
        self.exemplar = exemplar

    def analyze(self):
        return True

    def plan(self):
        self.update_adaptation_data("x", 1)
        self.update_adaptation_data("y", 4)
        return True

class TestGoalManagementInit(unittest.TestCase):
    """
    Test cases for the GoalManagement class using the DemoGoalManagement.
    """

    def setUp(self):
        self.goal_manager = None
        self.exemplar = None
        self.strategy = None

    def tearDown(self):
        self.goal_manager = None
        self.exemplar = None
        self.strategy = None

    def test_init_successfully(self):
        self.exemplar = DemoExemplar(auto_start=False)
        self.goal_manager = DemoGoalManagement(self.exemplar, {
            "adapt": {
                "strategies": [DemoStrategy(self.exemplar), FixedStrategy(self.exemplar)],
            }
        })
        self.assertIsInstance(self.goal_manager, GoalManagement)

    def test_init_with_invalid_strategies(self):
        self.exemplar = DemoExemplar(auto_start=False)
        with self.assertRaises(TypeError):
            self.goal_manager = DemoGoalManagement(self.exemplar, {
                "adapt": {
                    "active": True,
                    "priority": 1,
                    "strategies": [DemoStrategy(self.exemplar), "invalid"],
                }
            })

    def test_init_with_uninstantiated_strategies(self):
        self.exemplar = DemoExemplar(auto_start=False)
        with self.assertRaises(TypeError):
            self.goal_manager = DemoGoalManagement(self.exemplar, {
                "adapt": {
                    "active": True,
                    "priority": 1,
                    "strategies": [DemoStrategy, FixedStrategy],
                }
            })

class TestGoalManagementStrategiesAndTriggers(unittest.TestCase):
    """
    Test cases for the GoalManagement class using the DemoGoalManagement.
    """

    def setUp(self):
        self.goal_manager = None
        self.exemplar = None
        self.strategy = None

    def tearDown(self):
        self.goal_manager = None
        self.exemplar = None
        self.strategy = None

    def test_get_strategies_successfully(self):
        self.exemplar = DemoExemplar(auto_start=False)
        self.goal_manager = DemoGoalManagement(self.exemplar, {
            "adapt": {
                "strategies": [DemoStrategy(self.exemplar), FixedStrategy(self.exemplar)],
            }
        })
        strategies = self.goal_manager.get_strategies({"errors": [], "state": ""})
        self.assertIsInstance(strategies, list)
        self.assertTrue(all(isinstance(strategy, Strategy) for strategy in strategies))

    def test_set_goal_trigger(self):
        self.exemplar = DemoExemplar(auto_start=False)
        self.goal_manager = DemoGoalManagement(self.exemplar, {
            "adapt": {
                "strategies": [DemoStrategy(self.exemplar), FixedStrategy(self.exemplar)],
            }
        })
        self.goal_manager.set_goal_trigger("trigger", "adapt", False, TypeError)
        self.assertEqual(self.goal_manager._triggers["trigger"], {"goal": "adapt", "setTo": False, "exceptionClass": TypeError})

    def test_remove_goal_trigger(self):
        self.exemplar = DemoExemplar(auto_start=False)
        self.goal_manager = DemoGoalManagement(self.exemplar, {
            "adapt": {
                "strategies": [DemoStrategy(self.exemplar), FixedStrategy(self.exemplar)],
            }
        })
        self.goal_manager.set_goal_trigger("trigger", "adapt", False, TypeError)
        self.goal_manager.remove_goal_trigger("trigger")
        self.assertNotIn("trigger", self.goal_manager._triggers)

    def test_handle_errors(self):
        self.exemplar = DemoExemplar(auto_start=False)
        self.goal_manager = DemoGoalManagement(self.exemplar, {
            "adapt": {
                "strategies": [DemoStrategy(self.exemplar), FixedStrategy(self.exemplar)],
            }
        })
        self.goal_manager.set_goal_trigger("trigger", "adapt", False, TypeError)
        self.goal_manager.handle_errors({"errors": [TypeError()], "state": ""})
        self.assertFalse(self.goal_manager.goals_dict["adapt"]["active"])

    def test_handle_errors_with_no_trigger(self):
        self.exemplar = DemoExemplar(auto_start=False)
        self.goal_manager = DemoGoalManagement(self.exemplar, {
            "adapt": {
                "strategies": [DemoStrategy(self.exemplar), FixedStrategy(self.exemplar)],
            }
        })
        self.goal_manager.handle_errors({"errors": [TypeError()], "state": ""})
        self.assertTrue(self.goal_manager.goals_dict["adapt"]["active"])

    def test_handle_errors_with_no_errors(self):
        self.exemplar = DemoExemplar(auto_start=False)
        self.goal_manager = DemoGoalManagement(self.exemplar, {
            "adapt": {
                "strategies": [DemoStrategy(self.exemplar), FixedStrategy(self.exemplar)],
            }
        })
        self.goal_manager.set_goal_trigger("trigger", "adapt", False, TypeError)
        self.goal_manager.handle_errors({"errors": [], "state": ""})
        self.assertTrue(self.goal_manager.goals_dict["adapt"]["active"])

    def test_handle_errors_with_no_triggers(self):
        self.exemplar = DemoExemplar(auto_start=False)
        self.goal_manager = DemoGoalManagement(self.exemplar, {
            "adapt": {
                "strategies": [DemoStrategy(self.exemplar), FixedStrategy(self.exemplar)],
            }
        })
        self.goal_manager.handle_errors({"errors": [TypeError()], "state": ""})
        self.assertTrue(self.goal_manager.goals_dict["adapt"]["active"])

    def test_get_strategies_with_trigger_and_errors(self):
        self.exemplar = DemoExemplar(auto_start=False)
        self.goal_manager = DemoGoalManagement(self.exemplar, {
            "adapt": {
                "strategies": [DemoStrategy(self.exemplar), FixedStrategy(self.exemplar)],
            }
        })
        self.goal_manager.set_goal_trigger("trigger", "adapt", False, TypeError)
        strategies = self.goal_manager.get_strategies({"errors": [TypeError()], "state": ""})
        self.assertIsInstance(strategies, list)
        self.assertTrue(len(strategies) == 0)
        self.assertFalse(self.goal_manager.goals_dict["adapt"]["active"])


class TestGoalManagementResolveConflicts(unittest.TestCase):
    """
    Test cases for the GoalManagement class using the DemoGoalManagement.
    """

    def setUp(self):
        self.goal_manager = None
        self.exemplar = DemoExemplar(auto_start=True)

    def tearDown(self):
        self.goal_manager = None
        self.exemplar = None
        self.strategy = None

    def test_resolve_conflicts_successfully(self):
        self._start_server_and_wait_until_is_up()
        self.goal_manager = DemoGoalManagement(self.exemplar, {
            "adapt": {
                "strategies": [DemoStrategy(self.exemplar), FixedStrategy(self.exemplar)],
            }
        })
        self.exemplar.get_monitor_schema()
        self.exemplar.monitor()
        strategies = self.goal_manager.get_strategies({"errors": [], "state": ""})
        for strategy in strategies:
            if strategy.analyze():
                if strategy.plan():
                    execute = True
        conflicts = self.exemplar.check_for_update_conflicts()
        print(conflicts)
        self.goal_manager.resolve_conflicts(conflicts)
        self.assertEqual(self.exemplar.knowledge.plan_data, {"x": 1, "y": 4})

    def test_resolve_conflicts_with_more_than_two_conflicts(self):
        self._start_server_and_wait_until_is_up()
        self.exemplar = DemoExemplar(auto_start=False)
        self.goal_manager = DemoGoalManagement(self.exemplar, {
            "adapt": {
                "strategies": [DemoStrategy(self.exemplar), FixedStrategy(self.exemplar), DemoStrategy(self.exemplar)],
            }
        })
        self.exemplar.get_monitor_schema()
        self.exemplar.monitor()
        strategies = self.goal_manager.get_strategies({"errors": [], "state": ""})
        for strategy in strategies:
            if strategy.analyze():
                if strategy.plan():
                    execute = True
        conflicts = self.exemplar.check_for_update_conflicts()
        self.goal_manager.resolve_conflicts(conflicts)
        self.assertEqual(self.exemplar.knowledge.plan_data, { "x": 2, "y": 5 })

    def test_resolve_conflicts_with_no_conflicts(self):
        self._start_server_and_wait_until_is_up()
        self.exemplar = DemoExemplar(auto_start=False)
        self.goal_manager = DemoGoalManagement(self.exemplar, {
            "adapt": {
                "strategies": [DemoStrategy(self.exemplar)],
            }
        })
        self.exemplar.get_monitor_schema()
        self.exemplar.monitor()
        strategies = self.goal_manager.get_strategies({"errors": [], "state": ""})
        for strategy in strategies:
            if strategy.analyze():
                if strategy.plan():
                    execute = True
        conflicts = self.exemplar.check_for_update_conflicts()
        self.goal_manager.resolve_conflicts(conflicts)
        self.assertEqual(self.exemplar.knowledge.plan_data, { "x": 2, "y": 5 })

    def test_resolve_conflicts_with_triggers(self):
        self._start_server_and_wait_until_is_up()
        self.exemplar = DemoExemplar(auto_start=False)
        self.goal_manager = DemoGoalManagement(self.exemplar, {
            "adapt": {
                "strategies": [DemoStrategy(self.exemplar)],
            },
            "second_adapt": {
                "strategies": [FixedStrategy(self.exemplar)],
            }
        })
        # This trigger turns off the "second_adapt" goal, so the FixedStrategy should not be executed
        self.goal_manager.set_goal_trigger("trigger", "second_adapt", False, TypeError)
        self.exemplar.get_monitor_schema()
        self.exemplar.monitor()
        strategies = self.goal_manager.get_strategies({"errors": [TypeError()], "state": ""})
        for strategy in strategies:
            if strategy.analyze():
                if strategy.plan():
                    execute = True
        conflicts = self.exemplar.check_for_update_conflicts()
        self.goal_manager.resolve_conflicts(conflicts)
        self.assertEqual(self.exemplar.knowledge.plan_data, { "x": 2, "y": 5 }) # DemoStrategy should be executed

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