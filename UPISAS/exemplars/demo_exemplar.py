from time import sleep

from UPISAS import get_response_for_get_request
from UPISAS.exemplar import Exemplar
from UPISAS.exceptions import ServerNotReachable


class DemoExemplar(Exemplar):
    """
    A class which encapsulates a self-adaptive exemplar run in a docker container.
    """
    def __init__(self, auto_start=False, container_name="upisas-demo"):
        docker_config = {
            "name":  container_name,
            "image": "iliasger/upisas-demo-managed-system",
            "ports" : {3000: 3000}}

        super().__init__("http://localhost:3000", docker_config, auto_start)

    def start_run(self, app):
        self.exemplar_container.exec_run(cmd = f' sh -c "cd /usr/src/app && node {app}" ', detach=True)

    def stop_run(self):
        self.stop_container(remove=False)

    def stop_and_remove(self):
        self.stop_container(remove=True)

    def wait_for_server(self):
        while True:
            try:
                get_response_for_get_request(self.base_endpoint)
                break
            except ServerNotReachable as e:
                pass
            sleep(1)
