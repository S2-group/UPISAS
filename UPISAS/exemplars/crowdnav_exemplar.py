import pprint, time
from UPISAS.exemplar import Exemplar
import logging
pp = pprint.PrettyPrinter(indent=4)
logging.getLogger().setLevel(logging.INFO)

# TODO add actual exemplar name
class CrowdNavExemplar(Exemplar):
    """
    A class which encapsulates a self-adaptive exemplar run in a docker container.
    """
    _container_name = ""
    def __init__(self, auto_start=True):
        my_docker_kwargs = {
            "name":  "crowdnavgreen",    # TODO add your container name
            "image": "tasbiha/crowdnavgreenteam", # TODO add your exemplar's image name
            "ports" : {5000:3000}}              # TODO add any other necessary ports

        super().__init__("http://localhost:3000", my_docker_kwargs, auto_start)
    
    def start_run(self):
        time.sleep(5)
        pass 
