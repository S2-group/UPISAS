from UPISAS.goal_management import GoalManagement

class DemoGoalManagement(GoalManagement):
    def resolve_conflicts(self, conflicts):
        # Implement resolution for conflicts
        if not conflicts:
            return
        
        print(f"[Conflict Resolution]: Resolving {len(conflicts)} conflicts...")
        for conflict in conflicts:
            print(conflict)
            # Anything can be used, for this example we will use the new value
            self.exemplar.knowledge.plan_data[conflict["key"]] = conflict["new_value"]


# =================================================================================================
# Fish Finder Goal Management
class DemoFishFinderManagement(GoalManagement):
    """
    This class can be implemented in one of two ways to deal with collisions between strategies:
    1. The developer can re-implement the 'get_strategies' method to return a list of strategies 
        based on the current state of the system. e.g. if a goal with a high enough priority is
        active, then only the strategies for that goal should be returned.
    or,
    2. The developer can specify the logic for the 'resolve_conflicts' method to resolve conflicts
        between the strategies in the list. e.g. if two strategies are in conflict, the developer 
        can choose which strategy to use, take the average of the values, etc.
    """

    def resolve_conflicts(self, conflicts):
        # Implement resolution for conflicts
        if not conflicts:
            return
        
        # First, sort the conflicts based on the new_strategy's priority,
        # Highest priority first
        conflicts.sort(key=lambda x: x["new_strategy"].priority, reverse=True)
        
        # Apply the conflicts, discarding the lower priority strategies
        print(f"[Conflict Resolution]: Resolving {len(conflicts)} conflicts...")
        for conflict in conflicts:
            print(conflict)
            if conflict["key"] not in self.exemplar.knowledge.plan_data:
                self.exemplar.knowledge.plan_data[conflict["key"]] = conflict["new_value"]

        self.exemplar.knowledge.change_pipeline.clear()