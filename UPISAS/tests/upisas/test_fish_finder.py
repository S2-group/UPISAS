import unittest
import time

from UPISAS.goal_managers.demo_manager import DemoFishFinderManagement
from UPISAS.exemplars.demo_exemplar import DemoFishFinderExemplar
from UPISAS.strategies.demo_strategy import (
  DemoFFSearchDepthStrategy,
  DemoFFSearchSpeedStrategy,
  DemoFFTrackingDepthStrategy,
  DemoFFTrackingSpeedStrategy,
  DemoFFLowBatteryStrategy,
  DemoFFCheckBatteryStrategy
)
from UPISAS.exceptions.demo_exceptions import FishFoundException, FishNotFoundException, LowBatteryException
from UPISAS import get_response_for_get_request

class FishFinder():
    exemplar = None
    goal_manager = None

    def __init__(self):
        # Define the exemplar...
        self.exemplar = DemoFishFinderExemplar(auto_start=True)

        # Define the goal manager including the strategies and the high-level goals...
        self.goal_manager = DemoFishFinderManagement(self.exemplar, {
            "fish_search": {
                "active": True, # This goal is active by default
                "strategies": [
                    DemoFFSearchDepthStrategy(self.exemplar), 
                    DemoFFSearchSpeedStrategy(self.exemplar)
                ],
            },
            "fish_tracking": {
                "active": False, # This goal is not active by default
                "strategies": [
                    DemoFFTrackingDepthStrategy(self.exemplar), 
                    DemoFFTrackingSpeedStrategy(self.exemplar)
                ],
            },
            "check_battery": {
                "priority": 70, # This goal has a higher priority
                "active": True, # This goal is active by default
                "strategies": [DemoFFCheckBatteryStrategy(self.exemplar)],  
            },
            "return_home": {
                "priority": 100, # This goal has the highest priority
                "active": False, # This goal is not active by default
                "strategies": [DemoFFLowBatteryStrategy(self.exemplar)],
            }
        })

        # For the goal manager to auto-select the most relevant goal, we need to set triggers...
        self.goal_manager.set_goal_trigger("Stop search", "fish_search", False, FishFoundException) # Turn off this goal
        self.goal_manager.set_goal_trigger("Fish found", "fish_tracking", True, FishFoundException) # Turn on this goal

        self.goal_manager.set_goal_trigger("Fish lost", "fish_tracking", False, FishNotFoundException) # Turn off this goal
        self.goal_manager.set_goal_trigger("Restarting search", "fish_search", True, FishNotFoundException) # Turn on this goal

        # Because one of the other strategies will still be active, this goal will take priority.
        # The implementation of the goal manager will resolve the conflict between the strategies
        # via the resolve_conflicts method.
        self.goal_manager.set_goal_trigger("Drop everything and return", "return_home", True, LowBatteryException) # Turn on this goal

    def setup(self):
        self.exemplar.get_monitor_schema()
        self.exemplar.get_adaptation_options_schema()
        self.exemplar.get_execute_schema()

    def disable_fish_movement(self):
        self.exemplar._perform_get_request("disableFishMovement")

    def strategize(self, errors=[]):
        should_execute = False
        strategies = self.goal_manager.get_strategies({"errors": errors, "state": ""})
        for strategy in strategies:
            if strategy.analyze():
                if strategy.plan():
                    should_execute = True
        return should_execute

    def adapt(self):
        should_execute = False
        self.exemplar.monitor()

        # It is possible that an error may be raised at any point, even during
        # handling of an error that has just been raised. This is why we need to
        # loop until we can successfully strategize without any errors, so that
        # the system can fully consider the current state of the system.
        adaptation_error = None
        while True:
            try:
                should_execute = self.strategize(errors=[adaptation_error] if adaptation_error else [])
                break
            except (FishFoundException, FishNotFoundException, LowBatteryException) as e:
                # Exceptions are raised when the fish is found or the battery is low
                if e == adaptation_error:
                    # Same error was raised again, break the loop
                    raise e
                adaptation_error = e
                print(f"==================================== An error occurred, reassessing: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")
                raise e

        # try:
        #     strategies = self.goal_manager.get_strategies({"errors": [], "state": ""})
        #     for strategy in strategies:
        #         if strategy.analyze():
        #             if strategy.plan():
        #                 should_execute = True
        # except (FishFoundException, FishNotFoundException, LowBatteryException) as e:
        #     # Exceptions are raised when the fish is found or the battery is low
        #     strategies = self.goal_manager.get_strategies({"errors": [e], "state": ""})
        #     for strategy in strategies:
        #         if strategy.analyze():
        #             if strategy.plan():
        #                 should_execute = True
        # except Exception as e:
        #     print(f"An error occurred: {e}")
        #     raise e
        
        if should_execute:
            conflicts = self.exemplar.check_for_update_conflicts()
            if conflicts:
                self.goal_manager.resolve_conflicts(conflicts)
            self.exemplar.execute(self.exemplar.knowledge.plan_data)
            self.exemplar.knowledge.plan_data.clear()
    

class TestFishFinder(unittest.TestCase):
    def setUp(self):
        self.ff = FishFinder()

    def tearDown(self):
        if self.ff.exemplar and self.ff.exemplar.exemplar_container:
            self.ff.exemplar.stop_container()

    def test_fish_finder_starts_successfully(self):
        self._start_server_and_wait_until_is_up()
        self.ff.setup()
        self.assertIsInstance(self.ff.exemplar, DemoFishFinderExemplar)
        self.assertIsInstance(self.ff.goal_manager, DemoFishFinderManagement)

    def test_single_execution_of_fish_finder(self):
        self._start_server_and_wait_until_is_up()
        self.ff.setup()
        self.ff.adapt()
        self.assertIsInstance(self.ff.exemplar, DemoFishFinderExemplar)
        self.assertIsInstance(self.ff.goal_manager, DemoFishFinderManagement)

    def test_multiple_executions_of_fish_finder(self):
        # After 5 executions, the drone should be at a depth of 5 meters and a speed of 1.5 m/s
        self._start_server_and_wait_until_is_up()
        self.ff.setup()
        for _ in range(5):
            self.ff.adapt()
        self.ff.exemplar.monitor()
        self.assertEqual(self.ff.exemplar.knowledge.monitored_data["depth"][-1], 5)
        self.assertEqual(self.ff.exemplar.knowledge.monitored_data["speed"][-1], 1.5)

    def test_drone_finds_fish_after_search(self):
        # The drone should find the fish after 50 executions and switch to the tracking goal
        self._start_server_and_wait_until_is_up()
        self.ff.disable_fish_movement()
        self.ff.setup()
        for _ in range(51):
            self.ff.adapt()
        self.assertTrue(self.ff.exemplar.knowledge.monitored_data["fishInView"])
        self.assertTrue(self.ff.goal_manager.goals_dict["fish_tracking"]["active"])
        self.assertFalse(self.ff.goal_manager.goals_dict["fish_search"]["active"])

    def test_drone_returns_home_after_battery_low(self):
        # The drone should reach low battery after 275 executions and use return_home
        # The calculation is: 50m / 5 = 10%, 1.5m/s = 0.3% per second, 10% + 0.3% * 275 = 92.5% used
        self._start_server_and_wait_until_is_up()
        self.ff.setup()
        for _ in range(275):
            self.ff.adapt()
        self.ff.exemplar.monitor()
        self.assertTrue(self.ff.goal_manager.goals_dict["return_home"]["active"])

    def _start_server_and_wait_until_is_up(self, base_endpoint="http://localhost:3000"):
        self.ff.exemplar.start_run()
        while True:
            time.sleep(1)
            print("trying to connect...")
            response = get_response_for_get_request(base_endpoint)
            print(response.status_code)
            if response.status_code < 400:
                return


if __name__ == "__main__":
    unittest.main()

