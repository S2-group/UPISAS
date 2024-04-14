from UPISAS.goal_management import GoalManagement

class DemoGoalManagement(GoalManagement):
    def get_strategies(self, context):
        # Implement selection for strategies based on context
        return self.strategies_list

    def resolve_conflicts(self, conflicts):
        # Implement resolution for conflicts
        for conflict in conflicts:
            # Anything can be used, for this example we will use the new value
            for strategy in conflict["strategies"]:
                self.exemplar.knowledge.plan_data[conflict["key"]] = conflict["new_value"]
        