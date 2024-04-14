from time import sleep
import requests

from UPISAS import get_response_for_get_request
from UPISAS.exemplar import Exemplar
from UPISAS.exceptions import ServerNotReachable


class MlopsExemplar(Exemplar):
    """
    A class which encapsulates a self-adaptive ml exemplar run in a docker container.
    """
    def __init__(self, auto_start=False, container_name="mlops"):
        docker_config = {
            "name":  container_name,
            "image": "joeldevelops/mlops-exemplar:latest",
            "ports" : {5001: 5001}}

        super().__init__("http://localhost:5001", docker_config, auto_start)

    def prepare_model(self):
        self.exemplar_container.exec_run(cmd = f' sh -c "cd /app && rm -rf mlops/models && mkdir mlops/models" ', detach=False)

    def start_run(self):
        self.exemplar_container.exec_run(cmd = f' sh -c "cd /app && poetry run gunicorn mlops.app:app -w 4 -b 0.0.0.0:5001 --timeout 500 --log-level debug --access-logfile logs --error-logfile elogs" ', detach=True)

    def stop_run(self):
        self.stop_container(remove=False)

    def stop_and_remove(self):
        self.stop_container(remove=True)

    def wait_for_server(self):
        while True:
            try:
                get_response_for_get_request(self.base_endpoint)
                break
            except Exception as e:
                print(e)
                pass
            sleep(2)

    def reset_email_data(self):
        response = requests.post(f"{self.base_endpoint}/reset", json={})
        return response
    
    def pretrain_model(self):
        response = requests.put(f"{self.base_endpoint}/execute", json={})
        print(response)
        return response
    
    def update_email_data(self):
        response = requests.post(f"{self.base_endpoint}/update", json={})
        return response
    
    def load_test_results(self, data):
        response = requests.post(f"{self.base_endpoint}/test", json=data)
        return response