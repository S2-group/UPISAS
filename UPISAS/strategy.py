from abc import ABC, abstractmethod
import requests
import pprint

import logging

pp = pprint.PrettyPrinter(indent=4)


class Strategy(ABC):

    def __init__(self, exemplar):
        self.exemplar = exemplar

    @property
    def knowledge(self):
        return self.exemplar.knowledge
    
    def update_adaptation_data(self, key, value):
        """Handles the update of the knowledge object, while considering collisions."""
        update = {
            "strategy": self.__class__.__name__,
            "key": key,
            "value": value
        }
        self.exemplar.knowledge.change_pipeline.append(update)

    @abstractmethod
    def analyze(self):
        """ ... """
        pass

    @abstractmethod
    def plan(self):
        """ ... """
        pass

