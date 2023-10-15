from abc import ABC, abstractmethod
import requests
from jsonschema import validate, exceptions
from Knowledge import Knowledge


class Strategy(ABC):

    def __init__(self, exemplar):
        self.exemplar = exemplar
        self.knowledge = Knowledge(dict(), dict(), dict())

    def monitor(self, endpoint_suffix="monitor"):
        url = '/'.join([self.exemplar.base_endpoint, endpoint_suffix])
        fresh_data = requests.get(url).json()
        print("[Monitor]\tgot fresh_data: " + str(fresh_data))
        try:
            validate(fresh_data, self.exemplar.monitor_schema)
        except exceptions.ValidationError as error:
            print("Error in validating monitoring schema" + str(error))
        finally:
            data = self.knowledge.monitored_data
            for key in list(fresh_data.keys()):
                if key not in data:
                    data[key] = []
                data[key].append(fresh_data[key])
            print("[Knowledge]\tdata monitored so far: " + str(self.knowledge.monitored_data))

    def execute(self, adaptation, endpoint_suffix="execute"):
        try:
            validate(adaptation, self.exemplar.potential_adaptations_schema_single)
        except exceptions.ValidationError as error:
            print("Error in validating monitoring schema" + str(error))
        finally:
            url = '/'.join([self.exemplar.base_endpoint, endpoint_suffix])
            requests.post(url, adaptation)
            print("[Execute]\tposted configuration: " + str(adaptation))

    @abstractmethod
    def analyze(self):
        """ ... """
        pass

    @abstractmethod
    def plan(self):
        """ ... """
        pass

