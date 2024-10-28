import pprint, time
from UPISAS.exemplar import Exemplar
import logging
pp = pprint.PrettyPrinter(indent=4)
logging.getLogger().setLevel(logging.INFO)


class SWIM(Exemplar):
    """
    A class which encapsulates a self-adaptive exemplar run in a docker container.
    """
    _container_name = ""
    def __init__(self, auto_start: "Whether to immediately start the container after creation" =False, container_name = "swim"
                 ):
        '''Create an instance of the SWIM exemplar'''
        swim_docker_kwargs = {
            "name":  container_name,
            "image": "egalberts/swim:http",
            "ports" : {5901: 5901, 6901: 6901, 3000: 3000, 4242: 4242}}

        super().__init__("http://localhost:3000", swim_docker_kwargs, auto_start)
    
    def start_run(self):
        self.exemplar_container.exec_run(cmd = ' sh -c "cd ~/seams-swim/swim_HTTP/simulations/swim/ && ./run.sh sim 1" ', detach=True)