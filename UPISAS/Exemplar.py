import requests, docker, pprint
from jsonschema import validate, exceptions
from rich.progress import Progress
from UPISAS.utils import show_progress, perform_get_request
import logging

pp = pprint.PrettyPrinter(indent=4)
logging.getLogger().setLevel(logging.INFO)

class Exemplar:
    """
    A class which encapsulates a self-adaptive exemplar run in a docker container.
    """
    _container_name = ""
    def __init__(self, base_endpoint: "string with the URL of the exemplar's HTTP server", \
                 image_name: "Name of the exemplar's docker image", \
                 container_name: "Name to give the docker container created of the image", \
                 auto_start: "Whether to immediately start the container after creation" =False):
        '''Create an instance of the Exemplar class'''
        self.potential_adaptations_schema_all = None
        self.potential_adaptations_schema_single = None
        self.potential_adaptations_values = None
        self.monitor_schema = None
        self.base_endpoint = base_endpoint
        self.image_name = image_name
        self.container_name = container_name
        self.docker_client = docker.from_env()
        if auto_start:
            self.start()
        self.get_adaptations()
        self.get_monitor_schema()



    def get_adaptations(self, endpoint_suffix: "API Endpoint" = "adaptations"):
        '''Queries the API of the dockerized exemplar for possible adaptations.
        Places the result in the potential_adaptations dictionaries of the class'''
        url = '/'.join([self.base_endpoint, endpoint_suffix])
        potential_adaptations = perform_get_request(url).json()
        self.potential_adaptations_schema_all = potential_adaptations["schema_all"]
        logging.info("potential_adaptations schema_all set to: ")
        pp.pprint(self.potential_adaptations_schema_all)
        self.potential_adaptations_schema_single = potential_adaptations["schema_single"]
        logging.info("potential_adaptations schema_single set to: ")
        pp.pprint(self.potential_adaptations_schema_single)
        self.potential_adaptations_values = potential_adaptations["values"]
        try:
            validate(self.potential_adaptations_values, self.potential_adaptations_schema_all)
        except exceptions.ValidationError as error:
            logging.info("Error in validating potential_adaptations schema" + str(error))
        finally:
           logging.info("potential_adaptations values set to: ")
           pp.pprint(potential_adaptations["values"])

    def get_monitor_schema(self, endpoint_suffix: "API Endpoint" = "monitor_schema"):
        '''Queries the API for a schema describing the monitoring info of the particular exemplar'''
        url = '/'.join([self.base_endpoint, endpoint_suffix])
        self.monitor_schema = perform_get_request(url).json()
        logging.info("monitor_schema set to: ")
        pp.pprint(self.monitor_schema)

    def start(self):
        '''Starts running the docker container made from the given image when constructing this class'''
        self.pull_image_if_needed()
        try:
            container, container_status  = self.get_container()
            if container_status == "running":
                logging.warning("container already running...")
            else:
                logging.info("starting container...")
                container.start()
        except docker.errors.NotFound as e:
            logging.warning(e)
            logging.info(f"creating new container '{self.container_name}'")
            self.docker_client.containers.run(
                self.image_name, detach=True, name=self.container_name, ports={5901: 5901, 6901: 6901})

    def stop(self):
        '''Stops the docker container made from the given image when constructing this class'''
        try:
            container, container_status = self.get_container()
            if container_status == "exited":
                logging.warning("container already stopped...")
            else:
                logging.info("stopping container...")
                container.stop()
        except docker.errors.NotFound as e:
            logging.warning(e)
            logging.warning("cannot stop container")

    def pause(self):
        '''Pauses a running docker container made from the given image when constructing this class'''
        try:
            container, container_status = self.get_container()
            if container_status == "running":
                logging.info("pausing container...")
                container.pause()
            elif container_status == "paused":
                logging.warning("container already paused...")
            else:
                logging.warning("cannot pause container since it's not running")
        except docker.errors.NotFound as e:
            logging.error(e)
            logging.error("cannot pause container")

    def unpause(self):
        '''Resumes a paused docker container made from the given image when constructing this class'''
        try:
            container, container_status = self.get_container()
            if container_status == "paused":
                logging.info("unpausing container...")
                container.unpause()
            elif container_status == "running":
                logging.warning("container already running (why unpause it?)...")
            else:
                logging.warning("cannot unpause container since it's not paused")
        except docker.errors.NotFound as e:
            logging.warning(e)
            logging.warning("cannot unpause container")

    def pull_image_if_needed(self):
        '''If it hasn't been already, downloads the docker image named during construction'''
        try:
            self.docker_client.images.get(self.image_name)
            logging.info(f"image '{self.image_name}' found")
        except docker.errors.ImageNotFound:
            logging.info(f"image '{self.image_name}' not found, pulling it")
            with Progress() as progress:
                for line in self.docker_client.api.pull(self.image_name, stream=True, decode=True):
                    show_progress(line, progress)

    def get_container(self):
        '''Handle of the container'''
        try:
            container = self.docker_client.containers.get(self.container_name)
            logging.info(f"container '{container.name}' found with status '{container.attrs['State']['Status']}'")
            return container, container.attrs['State']['Status']
        except docker.errors.NotFound:
            raise docker.errors.NotFound(f"container '{self.container_name}' not found")
