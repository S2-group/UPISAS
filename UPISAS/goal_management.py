from abc import ABC, abstractmethod
import logging
from UPISAS.exceptions import DockerImageNotFoundOnDockerHub
from UPISAS.knowledge import Knowledge

class GoalManagement(ABC):
    """
    A class which determines a list of strategies to return based on the current state of the system and any potential encountered errors.
    """
    def __init__(self, exemplar, goals_list, *strategies_list):
        self.exemplar = exemplar
        self.goals_list = goals_list
        self. strategies_list = strategies_list

    @abstractmethod
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
        """
        pass
    
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