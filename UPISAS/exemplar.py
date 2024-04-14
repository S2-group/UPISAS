import docker
from abc import ABC, abstractmethod
from rich.progress import Progress
from UPISAS import show_progress
import logging
from docker.errors import DockerException, APIError
from UPISAS.exceptions import DockerImageNotFoundOnDockerHub
from UPISAS.knowledge import Knowledge

import requests

from UPISAS.exceptions import EndpointNotReachable
from UPISAS import validate_schema

logging.getLogger().setLevel(logging.INFO)


class Exemplar(ABC):
    """
    A class which encapsulates a self-adaptive exemplar run in a docker container.
    """
    _container_name = ""
    def __init__(self, base_endpoint: "string with the URL of the exemplar's HTTP server", \
                 docker_kwargs,
                 auto_start: "Whether to immediately start the container after creation" =False,
                 ):
        '''Create an instance of the Exemplar class'''
        self.base_endpoint = base_endpoint
        image_name = docker_kwargs["image"]
        self._container_name = docker_kwargs["name"]
        image_owner = image_name.split("/")[0]
        self.knowledge = Knowledge(dict(), dict(), dict(), dict(), dict(), dict(), dict())
        try:
            docker_client = docker.from_env()
            try:
                docker_client.images.get(image_name)
                logging.info(f"image '{image_name}' found locally")
            except docker.errors.ImageNotFound:
                logging.info(f"image '{image_name}' not found locally")
                images_from_owner = docker_client.images.search(image_owner)
                if image_name.split(":")[0] in [i["name"] for i in images_from_owner]:
                    logging.info(f"image '{image_name}' found on DockerHub, pulling it")
                    with Progress() as progress:
                        for line in docker_client.api.pull(image_name, stream=True, decode=True):
                            show_progress(line, progress)
                else:
                    logging.error(f"image '{image_name}' not found on DockerHub, exiting!")
                    raise DockerImageNotFoundOnDockerHub
            try:
                self.exemplar_container = docker_client.containers.get(self._container_name)
                logging.info(f"container '{self._container_name}' found locally")
            except docker.errors.NotFound:
                logging.info(f"container '{self._container_name}' not found locally")
                docker_kwargs["detach"] = True
                self.exemplar_container = docker_client.containers.create(**docker_kwargs)
        except DockerException as e:
            # TODO: Properly catch various errors. Currently, a lot of errors might be caught here.
            # Please check the logs if that happens.
            raise e
        if auto_start:
            self.start_container()

    @abstractmethod
    def start_run(self):
        pass

    def _append_data(self, fresh_data):
        # recurse on list data
        if isinstance(fresh_data, list):
            for item in fresh_data:
                self._append_data(item)
        # append data instance to monitored data
        else:
            data = self.knowledge.monitored_data
            for key in list(fresh_data.keys()):
                if key not in data:
                    data[key] = []
                data[key].append(fresh_data[key])
            print("[Knowledge]\tdata monitored so far: " + str(self.knowledge.monitored_data))
        return True

    # Monitor lives in the Exemplar class because it is the Exemplar that is responsible for
    # interfacing with the monitored system.
    def monitor(self, endpoint_suffix="monitor", with_validation=True):
        fresh_data = self._perform_get_request(endpoint_suffix)
        print("[Monitor]\tgot fresh_data: " + str(fresh_data))
        if with_validation:
            validate_schema(fresh_data, self.knowledge.monitor_schema)
        self._append_data(fresh_data)
        return True

    # Similarly, execute also interfaces with the monitored system.
    def execute(self, adaptation, endpoint_suffix="execute", with_validation=True):
        if with_validation:
            validate_schema(adaptation, self.knowledge.execute_schema)
        url = '/'.join([self.exemplar.base_endpoint, endpoint_suffix])
        response = requests.put(url, json=adaptation)
        print("[Execute]\tposted configuration: " + str(adaptation))
        if response.status_code == 404:
            logging.error("Cannot execute adaptation on remote system, check that the execute endpoint exists.")
            raise EndpointNotReachable
        return True
    
    def get_adaptation_options(self, endpoint_suffix: "API Endpoint" = "adaptation_options", with_validation=True):
        self.knowledge.adaptation_options = self._perform_get_request(endpoint_suffix)
        if with_validation:
            validate_schema(self.knowledge.adaptation_options, self.knowledge.adaptation_options_schema)
        logging.info("adaptation_options set to: ")
        pp.pprint(self.knowledge.adaptation_options)

    def get_monitor_schema(self, endpoint_suffix = "monitor_schema"):
        self.knowledge.monitor_schema = self._perform_get_request(endpoint_suffix)
        logging.info("monitor_schema set to: ")
        pp.pprint(self.knowledge.monitor_schema)

    def get_execute_schema(self, endpoint_suffix = "execute_schema"):
        self.knowledge.execute_schema = self._perform_get_request(endpoint_suffix)
        logging.info("execute_schema set to: ")
        pp.pprint(self.knowledge.execute_schema)

    def get_adaptation_options_schema(self, endpoint_suffix: "API Endpoint" = "adaptation_options_schema"):
        self.knowledge.adaptation_options_schema = self._perform_get_request(endpoint_suffix)
        logging.info("adaptation_options_schema set to: ")
        pp.pprint(self.knowledge.adaptation_options_schema)

    def _perform_get_request(self, endpoint_suffix: "API Endpoint"):
        url = '/'.join([self.exemplar.base_endpoint, endpoint_suffix])
        response = get_response_for_get_request(url)
        if response.status_code == 404:
            logging.error("Please check that the endpoint you are trying to reach actually exists.")
            raise EndpointNotReachable
        return response.json()

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

    def stop_container(self, remove=True):
        '''Stops the docker container made from the given image when constructing this class'''
        try:
            container_status = self.get_container_status()
            if container_status == "exited":
                logging.warning("container already stopped...")
                if remove:
                    self.exemplar_container.remove()
                    self.exemplar_container = None
            else:
                logging.info("stopping container...")
                self.exemplar_container.stop()
                if remove:
                    self.exemplar_container.remove()
                    self.exemplar_container = None
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
        if self.exemplar_container:
            self.exemplar_container.reload()
            return self.exemplar_container.status
        return "removed"
