import docker, pprint
from rich.progress import Progress
from UPISAS import show_progress, perform_get_request, validate_schema
from UPISAS.exemplar import Exemplar
import logging
from docker.errors import DockerException
pp = pprint.PrettyPrinter(indent=4)
logging.getLogger().setLevel(logging.INFO)
import time



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
    #docker exec -it swim sh -c "cd ~/seams-swim/swim/simulations/swim/ && ./run.sh sim 1"
        print("doing something")
        self.exemplar_container.exec_run(cmd = ' sh -c "cd ~/seams-swim/swim_HTTP/simulations/swim/ && ./run.sh sim 1" ', detach=True)

        time.sleep(10)
        input("proceed to ask for stuff programmatically")

        #self.get_adaptations()
        self.get_monitor_schema()