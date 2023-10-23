from UPISAS.exemplar import Exemplar


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
