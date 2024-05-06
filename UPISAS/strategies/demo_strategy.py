import math
from UPISAS.strategy import Strategy
from UPISAS.exceptions.demo_exceptions import FishFoundException, FishNotFoundException, LowBatteryException


class DemoStrategy(Strategy):

    def analyze(self):
        data = self.knowledge.monitored_data
        print(data)
        mean_f = sum(data["f"])/len(data["f"])
        print("[Analysis]\tmean_f: " + str(mean_f))
        if mean_f > 0:
            self.knowledge.analysis_data["mean_f"] = mean_f
            return True
        return False

    def plan(self):
        data = self.knowledge.analysis_data["mean_f"]
        if data > 0:
            self.update_adaptation_data("x", 2)
            self.update_adaptation_data("y", 5)
            return True
        return False

# =================================================================================================
# Fish Finder Strategies
class DemoFFTrackingDepthStrategy(Strategy):
    """
    Strategy for tracking the depth of the fish compared with the drone to keep the fish in view.
    """
    priority = 10
    fish_previously_seen = False # With this an exception can be raised when the fish is lost

    def analyze(self):
        data = self.knowledge.monitored_data
        print(data)
        depth_dif = abs(data["fishDepth"][-1] - data["depth"][-1])
        print("[Analysis]\tdepth_dif: " + str(depth_dif))

        if data["fishInView"][-1]:
            if abs(data["fishDepth"][-1] - data["depth"][-1]) > 0:
                self.knowledge.analysis_data["depth_difference"] = data["fishDepth"][-1] - data["depth"][-1]

            return True
        elif self.fish_previously_seen:
            self.fish_previously_seen = False
            raise FishNotFoundException("Lost sight of fish.")
        return False

    def plan(self):
        data = self.knowledge.analysis_data
        if "depth_difference" in data and abs(data["depth_difference"]) > 1:
            depth_change = 1.0 if data["depth_difference"] > 0 else -1.0
            self.update_adaptation_data("depth", depth_change)
        elif "depth_difference" in data and abs(data["depth_difference"]) > 0:
            self.update_adaptation_data("depth", data["depth_difference"])
        else:
            self.update_adaptation_data("depth", 0)

        return True
    

class DemoFFTrackingSpeedStrategy(Strategy):
    """
    Strategy for tracking the speed of the fish compared with the drone to keep the fish in view.
    """
    priority = 10
    fish_previously_seen = False

    def analyze(self):
        data = self.knowledge.monitored_data
        print(data)
        speed_dif = abs(data["fishSpeed"][-1] - data["speed"][-1])
        print("[Analysis]\tspeed_dif: " + str(speed_dif))

        if data["fishInView"][-1]:
            if abs(data["fishSpeed"][-1] - data["speed"][-1]) > 0:
                self.knowledge.analysis_data["speed_difference"] = data["fishSpeed"][-1] - data["speed"][-1]

            return True
        elif self.fish_previously_seen:
            self.fish_previously_seen = False
            raise FishNotFoundException("Lost sight of fish.")
        return False

    def plan(self):
        data = self.knowledge.analysis_data
        if "speed_difference" in data and abs(data["speed_difference"]) > 1:
            speed_change = 1.0 if data["speed_difference"] > 0 else -1.0
            self.update_adaptation_data("speed", speed_change)
        elif "speed_difference" in data and abs(data["speed_difference"]) > 0:
            self.update_adaptation_data("speed", data["speed_difference"])
        else:
            self.update_adaptation_data("speed", 0)

        return True
    

class DemoFFSearchDepthStrategy(Strategy):
    """
    The fish is known to be at a depth of 50 meters. The drone should search for the fish at this depth
    first, before searching at other depths.
    """
    priority = 10
    reached_intended_depth = False
    reached_bottom = False

    def analyze(self):
        data = self.knowledge.monitored_data
        print(data)
        print("[Analysis]\current_depth: " + str(data["depth"][-1]))
        self.knowledge.analysis_data["current_depth"] = data["depth"][-1]

        if data["fishInView"][-1]:
            raise FishFoundException("Fish found.")
        
        if data["depth"][-1] >= 50:
            self.reached_intended_depth = True

        if self.reached_intended_depth:
            # If we've reached this point, the fish is not at the intended depth,
            # so we should search lower.
            return True

        return True

    def plan(self):
        current_depth = self.knowledge.analysis_data["current_depth"]
        # Move at the top speed to the intended depth, then move slower to search
        depth_change = 0.65 if self.reached_intended_depth else 1.0

        if current_depth >= 99:
            self.reached_bottom = True

        if current_depth <= 5:
            self.reached_bottom = False

        if self.reached_bottom:
            depth_change = depth_change * -1

        self.update_adaptation_data("depth", depth_change)

        return True
    

class DemoFFSearchSpeedStrategy(Strategy):
    """
    The fish is known to be at a speed of 1.5 m/s. The drone should search for the fish at this speed
    first, before searching at other speeds.
    """
    priority = 10

    def analyze(self):
        data = self.knowledge.monitored_data
        print(data)
        print("[Analysis]\current_speed: " + str(data["speed"][-1]))

        if data["fishInView"][-1]:
            raise FishFoundException("Fish found.")

        return True

    def plan(self):
        # Move at the top speed to the intended speed, then move slower to search
        data = self.knowledge.monitored_data
        if data["speed"][-1] < 1.5:
            speed_change = 1.0 if data["speed"][-1] < 1.0 else 0.5
            self.update_adaptation_data("speed", speed_change)
        else:
            self.update_adaptation_data("speed", 0)

        return True
    

class DemoFFCheckBatteryStrategy(Strategy):
    """
    The drone should constantly check the battery level and throw an 
    exception if the battery level is too low.
    """
    priority = 60
    lower_threshold_reached = False

    def analyze(self):
        # Check the battery level and see how much battery it will take to reach the surface
        # and if it's possible to reach the surface with the current battery level.
        data = self.knowledge.monitored_data
        print(data)
        print("[Analysis]\tbattery_level: " + str(data["battery"][-1]))

        if data["depth"][-1] > 0:
            percent_to_surface = data["depth"][-1] / 5
            percent_at_current_speed = data["speed"][-1] / 5
            battery_required = percent_to_surface + percent_at_current_speed
            battery_level = data["battery"][-1]
            if battery_level <= battery_required:
                # Only raise the exception once
                if not self.lower_threshold_reached:
                    self.lower_threshold_reached = True
                    raise LowBatteryException("Low battery level.")
        
        return False

    def plan(self):
        return True
    

class DemoFFLowBatteryStrategy(Strategy):
    """
    The drone should attempt to reach the surface if the battery level is low.
    """
    # Functionally a static variable
    priority = 100

    def analyze(self):
        # Check the battery level and see how much battery it will take to reach the surface
        # and if it's possible to reach the surface with the current battery level.
        data = self.knowledge.monitored_data
        print(data)
        print("[Analysis]\tbattery_level: " + str(data["battery"][-1]))
        print("[Analysis]\tdepth: " + str(data["depth"][-1]))
        print("[Analysis]\tspeed: " + str(data["speed"][-1]))

        if data["depth"][-1] > 0:
            percent_to_surface = data["depth"][-1] / 5
            percent_at_current_speed = data["speed"][-1] / 5
            battery_required = percent_to_surface + percent_at_current_speed
            battery_level = data["battery"][-1]
            
            self.knowledge.analysis_data["battery_required"] = battery_required
            self.knowledge.analysis_data["battery_level"] = battery_level
            return True

    def plan(self):
        # Move at the top speed to the surface
        data = self.knowledge.analysis_data
        monitor_data = self.knowledge.monitored_data
        if data["battery_level"] > data["battery_required"]:
            self.update_adaptation_data("depth", -1)
        else:
            # There is not enough battery to reach the surface
            # attempt to reach the surface at a slower speed
            speed_change = -1.0 if monitor_data["speed"][-1] >= 2.0 else 1.0 - monitor_data["speed"][-1]
            self.update_adaptation_data("speed", speed_change)
            self.update_adaptation_data("depth", -1)
            
        return True