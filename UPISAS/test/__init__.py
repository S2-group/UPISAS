from subprocess import Popen
import time

from UPISAS import perform_get_request
from UPISAS.example_strategy import ExampleStrategy
from UPISAS.exemplar import Exemplar


def create_strategy(nodejs_file, base_endpoint, image_name, container_name):
    proc = Popen(['node', nodejs_file, '-d'])
    time.sleep(1)
    exemplar = Exemplar(base_endpoint, image_name, container_name, auto_start=True)
    strategy = ExampleStrategy(exemplar)
    return proc, exemplar, strategy


def create_server_process(nodejs_file):
    proc = Popen(['node', nodejs_file, '-d'])
    while True:
        time.sleep(1)
        print("trying to connect...")
        try:
            _, status_code = perform_get_request("http://localhost:3000")
            print(status_code)
            if status_code < 400:
                break
        except:
            print('exceppttt')
            pass
    return proc
