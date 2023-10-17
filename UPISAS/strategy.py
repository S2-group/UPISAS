from abc import ABC, abstractmethod
import requests
from UPISAS.knowledge import Knowledge
from UPISAS import perform_get_request, validate_schema
import logging


class Strategy(ABC):

    def __init__(self, exemplar):
        self.exemplar = exemplar
        self.knowledge = Knowledge(dict(), dict(), dict())

    def monitor(self, endpoint_suffix="monitor"):
        url = '/'.join([self.exemplar.base_endpoint, endpoint_suffix])
        response, status_code = perform_get_request(url)
        if status_code == 404:
            logging.info("Cannot retrieve data, check that the monitor endpoint exists.")
            return False
        fresh_data = response.json()
        print("[Monitor]\tgot fresh_data: " + str(fresh_data))
        validate_schema(fresh_data, self.exemplar.monitor_schema)
        data = self.knowledge.monitored_data
        for key in list(fresh_data.keys()):
            if key not in data:
                data[key] = []
            data[key].append(fresh_data[key])
        print("[Knowledge]\tdata monitored so far: " + str(self.knowledge.monitored_data))
        return True

    def execute(self, adaptation, endpoint_suffix="execute"):
        validate_schema(adaptation, self.exemplar.potential_adaptations_schema_single)
        url = '/'.join([self.exemplar.base_endpoint, endpoint_suffix])
        response = requests.post(url, adaptation)
        print("[Execute]\tposted configuration: " + str(adaptation))
        if response.status_code == 404:
            logging.info("Cannot execute adaptation on remote system, check that the execute endpoint exists.")
            return False
        return True

    @abstractmethod
    def analyze(self):
        """ ... """
        pass

    @abstractmethod
    def plan(self):
        """ ... """
        pass

