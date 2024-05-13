from abc import ABC, abstractmethod
import logging
from UPISAS.exceptions import DockerImageNotFoundOnDockerHub
from UPISAS.knowledge import Knowledge
from UPISAS.strategy import Strategy

class GoalManagement(ABC):
    """
    A class which determines a list of strategies to return based on the current state of the system and any potential encountered errors.
    """
    def __init__(self,
                 exemplar: "Instantiated Exemplar object", 
                 goals_dict: "dict of goals and their related strategies"):
        """
        Initializes the GoalManagement object with the exemplar and goals_dict.

        The goals_dict parameter is a dictionary with the following shape:
        {
          "goal1": {
              "active": "(optional) boolean representing if the goal is active, defaults to true",
              "priority": "(optional) int representing the priority of the goal",
              "strategies": [strategy1, strategy2, ...]
          },
          "goal2": { ... },
          ...
        }

        Note that the strategies in the goals_dict should be instantiated objects of the Strategy class.
        """
        self.exemplar = exemplar
        self.goals_dict = goals_dict
        self._triggers = {}
        for goal, goal_dict in self.goals_dict.items():
            goal_dict["active"] = goal_dict.get("active", True)
            goal_dict["priority"] = goal_dict.get("priority", 0)
            for strategy in goal_dict["strategies"]:
                if not isinstance(strategy, Strategy):
                    raise TypeError(f"Strategy {strategy} is not an instance of Strategy")

    def set_goal_trigger(self,
                         name: "str representing the trigger name. Must be unique.",
                         goal: "str representing the goal", 
                         setTo: "bool representing the future state of the goal",
                         exceptionClass: "exception class representing the trigger"):
        """
        Sets the trigger for the goal in the goals_dict.

        Ex: When setting a goal, this method allows for goals to be automatically 
        triggered based on the state of the system. If the exception shows up in
        the context object, then the trigger will be raised and the goal will be 
        activated by setting its "active" field to True.
        """
        if goal not in self.goals_dict:
            logging.error(f"Goal {goal} not found in goals_dict")
            return
        
        self._triggers[name] = {"goal": goal, "setTo": setTo, "exceptionClass": exceptionClass}

    def remove_goal_trigger(self,
                            name: "str representing the trigger name"):
        """
        Removes the trigger for the goal in the goals_dict.
        """
        if name not in self._triggers:
            logging.error(f"Trigger {name} not found in triggers")
            return
        
        del self._triggers[name]

    def handle_errors(self, context: "dict with the current state of the system"):
        """
        Updates the active state of the goals in goals_dict based on the context data.
        """
        for trigger in self._triggers.values():
            for error in context["errors"]:
                if isinstance(error, trigger["exceptionClass"]):
                    self.goals_dict[trigger["goal"]]["active"] = trigger["setTo"]

    def get_strategies(self, 
                       context: "dict with the current state of the system"
                       ) -> "list of Strategy objects":
        """
        User-implemented method to return a list of strategies based on the current 
        state of the system. The context parameter is a dictionary with the current 
        state of the system, and should ideally contain the following shape:
        {
          "errors": "list of encountered errors",
          "state": "current state of the system 
                    (data other than knowledge, which is in self.exemplar.knowledge)",
        }

        If not overridden, this method will return a list of the active goal strategies.
        """
        self.handle_errors(context)
        strategies = []
        for goal, goal_dict in self.goals_dict.items():
            if goal_dict.get("active", True):
                strategies.extend(goal_dict["strategies"])
        return strategies
    
    @abstractmethod
    def resolve_conflicts(self, 
                          conflicts: "list of dicts with the encountered conflicts between the strategies in the list"
                          ) -> "list of Strategy objects":
        """
        User-implemented method to resolve conflicts between the strategies in the 
        list. The strategies parameter is a list of Strategy objects, and should 
        update the exemplar knowledge plan_data prior to exiting.

        The conflicts parameter is a list of dictionaries with the following shape:
        [
          {
            "strategies": "list of strategies in conflict",
            "key": "dict key in the plan_data that is in conflict",
            "original_value": "value of the conflict",
            "new_value": "new value to resolve the conflict",
          },
          ...
        ]
        """
        pass