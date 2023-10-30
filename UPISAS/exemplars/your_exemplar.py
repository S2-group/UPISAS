import pprint, time
from UPISAS.exemplar import Exemplar
import logging
pp = pprint.PrettyPrinter(indent=4)
logging.getLogger().setLevel(logging.INFO)

# TODO add actual exemplar name
class YourExemplar(Exemplar):
    """
    A class which encapsulates a self-adaptive exemplar run in a docker container.
    """
    _container_name = ""
    def __init__(self, auto_start: "Whether to immediately start the container after creation" =False):
        my_docker_kwargs = {
            "name":  "<your container name>",    # TODO add your container name
            "image": "<user name>/<image name>", # TODO add your exemplar's image name
            "ports" : {3000: 3000}}              # TODO add any other necessary ports

        super().__init__("http://localhost:3000", my_docker_kwargs, auto_start)
    
    def start_run(self):
        pass
        # TODO start a simulation run within the exemplar's container (see swim.py)
