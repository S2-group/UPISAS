import docker, pprint
from rich.progress import Progress
from UPISAS import show_progress, perform_get_request, validate_schema
import logging
from docker.errors import DockerException
pp = pprint.PrettyPrinter(indent=4)
logging.getLogger().setLevel(logging.INFO)


class Exemplar:
    """
    A class which encapsulates a self-adaptive exemplar run in a docker container.
    """
    _container_name = ""
    def __init__(self, base_endpoint: "string with the URL of the exemplar's HTTP server", \
                 docker_kwargs,
                 auto_start: "Whether to immediately start the container after creation" =False,
                 ):
        '''Create an instance of the Exemplar class'''
        self.potential_adaptations_schema_all = None
        self.potential_adaptations_schema_single = None
        self.potential_adaptations_values = None
        self.monitor_schema = None
        self.base_endpoint = base_endpoint

        image_name = docker_kwargs["image"]
        try:
            docker_client = docker.from_env()
            try:
                docker_client.images.get(image_name)
                logging.info(f"image '{image_name}' found")
            except docker.errors.ImageNotFound:
                logging.info(f"image '{image_name}' not found, pulling it")
                with Progress() as progress:
                    for line in docker_client.api.pull(image_name, stream=True, decode=True):
                        show_progress(line, progress)
            docker_kwargs["detach"] = True
            self.exemplar_container = docker_client.containers.create(**docker_kwargs)
        except DockerException as dexcep:
            logging.warning("A DockerException occurred, are you sure Docker is running?")
            logging.error(dexcep)
            exit(42)
        if auto_start:
            self.start_container()

    def get_adaptations(self, endpoint_suffix: "API Endpoint" = "adaptations"):
        '''Queries the API of the dockerized exemplar for possible adaptations.
        Places the result in the potential_adaptations dictionaries of the class'''
        url = '/'.join([self.base_endpoint, endpoint_suffix])
        response, status_code = perform_get_request(url)
        if status_code == 404:
            logging.warning("Please check that the endpoint you are trying to reach actually exists.")
            exit(2)
        potential_adaptations = response.json()
        self.potential_adaptations_schema_all = potential_adaptations["schema_all"]
        logging.info("potential_adaptations schema_all set to: ")
        pp.pprint(self.potential_adaptations_schema_all)
        self.potential_adaptations_schema_single = potential_adaptations["schema_single"]
        logging.info("potential_adaptations schema_single set to: ")
        pp.pprint(self.potential_adaptations_schema_single)
        self.potential_adaptations_values = potential_adaptations["values"]
        validate_schema(self.potential_adaptations_values, self.potential_adaptations_schema_all)
        logging.info("potential_adaptations values set to: ")
        pp.pprint(potential_adaptations["values"])

    def get_monitor_schema(self, endpoint_suffix: "API Endpoint" = "monitor_schema"):
        '''Queries the API for a schema describing the monitoring info of the particular exemplar'''
        url = '/'.join([self.base_endpoint, endpoint_suffix])
        response, status_code = perform_get_request(url)
        if status_code == 404:
            logging.warning("Please check that the endpoint you are trying to reach actually exists.")
            exit(3)
        self.monitor_schema = response.json()
        logging.info("monitor_schema set to: ")
        pp.pprint(self.monitor_schema)

    def start_container(self):
        '''Starts running the docker container made from the given image when constructing this class'''
        try:
            container_status = self.get_container_status()
            if container_status == "running":
                logging.warning("container already running...")
            else:
                logging.info("starting container...")
                self.exemplar_container.start()
            return True
        except docker.errors.NotFound as e:
            logging.error(e)
            # logging.info(f"creating new container '{self.container_name}'")
            # self.docker_client.containers.run(
            #     self.image_name, detach=True, name=self.container_name, ports={5901: 5901, 6901: 6901})

    def stop_container(self, remove=True):
        '''Stops the docker container made from the given image when constructing this class'''
        try:
            container_status = self.get_container_status()
            if container_status == "exited":
                logging.warning("container already stopped...")
                if remove is True: self.exemplar_container.remove()
            else:
                logging.info("stopping container...")
                self.exemplar_container.stop()
                if remove is True: self.exemplar_container.remove()
            return True
        except docker.errors.NotFound as e:
            logging.warning(e)
            logging.warning("cannot stop container")

    def pause_container(self):
        '''Pauses a running docker container made from the given image when constructing this class'''
        try:
            container_status = self.get_container_status()
            if container_status == "running":
                logging.info("pausing container...")
                self.exemplar_container.pause()
                return True
            elif container_status == "paused":
                logging.warning("container already paused...")
                return True
            else:
                logging.warning("cannot pause container since it's not running")
                return False
        except docker.errors.NotFound as e:
            logging.error(e)
            logging.error("cannot pause container")

    def unpause_container(self):
        '''Resumes a paused docker container made from the given image when constructing this class'''
        try:
            container_status = self.get_container_status()
            if container_status == "paused":
                logging.info("unpausing container...")
                self.exemplar_container.unpause()
                return True
            elif container_status == "running":
                logging.warning("container already running (why unpause it?)...")
                return True
            else:
                logging.warning("cannot unpause container since it's not paused")
                return False
        except docker.errors.NotFound as e:
            logging.warning(e)
            logging.warning("cannot unpause container")

    def get_container_status(self):
        self.exemplar_container.reload()
        return self.exemplar_container.status
