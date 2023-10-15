import requests, docker, pprint
from jsonschema import validate, exceptions
from rich.progress import Progress
import utils

pp = pprint.PrettyPrinter(indent=4)


class Exemplar:

    def __init__(self, base_endpoint, image_name, container_name, auto_start=False):
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

    def get_adaptations(self, endpoint_suffix="adaptations"):
        url = '/'.join([self.base_endpoint, endpoint_suffix])
        potential_adaptations = utils.perform_get_request(url).json()
        self.potential_adaptations_schema_all = potential_adaptations["schema_all"]
        print("potential_adaptations schema_all set to: ")
        pp.pprint(self.potential_adaptations_schema_all)
        self.potential_adaptations_schema_single = potential_adaptations["schema_single"]
        print("potential_adaptations schema_single set to: ")
        pp.pprint(self.potential_adaptations_schema_single)
        self.potential_adaptations_values = potential_adaptations["values"]
        try:
            validate(self.potential_adaptations_values, self.potential_adaptations_schema_all)
        except exceptions.ValidationError as error:
            print("Error in validating potential_adaptations schema" + str(error))
        finally:
           print("potential_adaptations values set to: ")
           pp.pprint(potential_adaptations["values"])

    def get_monitor_schema(self, endpoint_suffix="monitor_schema"):
        url = '/'.join([self.base_endpoint, endpoint_suffix])
        self.monitor_schema = utils.perform_get_request(url).json()
        # self.monitor_schema = requests.get(url).json()
        print("monitor_schema set to: ")
        pp.pprint(self.monitor_schema)

    def start(self):
        self.pull_image_if_needed()
        try:
            container, container_status  = self.get_container()
            if container_status == "running":
                print("container already running...")
            else:
                print("starting container...")
                container.start()
        except docker.errors.NotFound as e:
            print(e)
            print(f"creating new container '{self.container_name}'")
            self.docker_client.containers.run(
                self.image_name, detach=True, name=self.container_name, ports={5901: 5901, 6901: 6901})

    def stop(self):
        try:
            container, container_status = self.get_container()
            if container_status == "exited":
                print("container already stopped...")
            else:
                print("stopping container...")
                container.stop()
        except docker.errors.NotFound as e:
            print(e)
            print("cannot stop container")

    def pause(self):
        try:
            container, container_status = self.get_container()
            if container_status == "running":
                print("pausing container...")
                container.pause()
            elif container_status == "paused":
                print("container already paused...")
            else:
                print("cannot pause container since it's not running")
        except docker.errors.NotFound as e:
            print(e)
            print("cannot pause container")

    def unpause(self):
        try:
            container, container_status = self.get_container()
            if container_status == "paused":
                print("unpausing container...")
                container.unpause()
            elif container_status == "running":
                print("container already running (why unpause it?)...")
            else:
                print("cannot unpause container since it's not paused")
        except docker.errors.NotFound as e:
            print(e)
            print("cannot unpause container")

    def pull_image_if_needed(self):
        try:
            self.docker_client.images.get(self.image_name)
            print(f"image '{self.image_name}' found")
        except docker.errors.ImageNotFound:
            print(f"image '{self.image_name}' not found, pulling it")
            with Progress() as progress:
                for line in self.docker_client.api.pull(self.image_name, stream=True, decode=True):
                    utils.show_progress(line, progress)

    def get_container(self):
        try:
            container = self.docker_client.containers.get(self.container_name)
            print(f"container '{container.name}' found with status '{container.attrs['State']['Status']}'")
            return container, container.attrs['State']['Status']
        except docker.errors.NotFound:
            raise docker.errors.NotFound(f"container '{self.container_name}' not found")
