import requests
import logging
from jsonschema import validate, exceptions

from UPISAS.exceptions import ServerNotReachable

pull_image_tasks = {}


def show_progress(line, progress):
    """ Show task progress (red for download, green for extract). Used when pulling images."""
    if line['status'] == 'Downloading':
        id = f'[red][Download {line["id"]}]'
    elif line['status'] == 'Extracting':
        id = f'[green][Extract  {line["id"]}]'
    else:
        # skip other statuses
        return
    if id not in pull_image_tasks.keys():
        pull_image_tasks[id] = progress.add_task(f"{id}", total=line['progressDetail']['total'])
    else:
        progress.update(pull_image_tasks[id], completed=line['progressDetail']['current'])


def perform_get_request(url):
    try:
        logging.info("GET request to " + str(url))
        response = requests.get(url)
        return response, response.status_code
    except requests.exceptions.ConnectionError as e:
        logging.warning(e)
        logging.warning("Please check that the server is reachable and retry.")
        raise ServerNotReachable()


def validate_schema(json_instance, json_schema):
    try:
        validate(json_instance, json_schema)
    except exceptions.ValidationError as error:
        logging.info("Error in validating '" + str(json_schema) + "' schema" + str(error))
