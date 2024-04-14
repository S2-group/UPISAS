from abc import ABC, abstractmethod
import requests
import pprint

from UPISAS.exceptions import EndpointNotReachable, ServerNotReachable
from UPISAS.knowledge import Knowledge
from UPISAS import validate_schema, get_response_for_get_request
import logging

pp = pprint.PrettyPrinter(indent=4)


class Strategy(ABC):

    def __init__(self, exemplar):
        self.exemplar = exemplar

    def ping(self):
        ping_res = self._perform_get_request(self.exemplar.base_endpoint)
        logging.info(f"ping result: {ping_res}")

    @property
    def knowledge(self):
        return self.exemplar.knowledge
    
    def update_knoweldge(self, key, value):
        self.exemplar.knowledge[key] = value

    @abstractmethod
    def analyze(self):
        """ ... """
        pass

    @abstractmethod
    def plan(self):
        """ ... """
        pass

