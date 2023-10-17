from subprocess import Popen
import time
from UPISAS.example_strategy import ExampleStrategy
from UPISAS.exemplar import Exemplar


def create_strategy(nodejs_file, base_endpoint, image_name, container_name):
    proc = Popen(['node', nodejs_file, '-d'])
    time.sleep(1)
    exemplar = Exemplar(base_endpoint, image_name, container_name, auto_start=True)
    strategy = ExampleStrategy(exemplar)
    return proc, exemplar, strategy
