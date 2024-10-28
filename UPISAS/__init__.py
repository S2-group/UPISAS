import jsonschema
import requests
import logging

from UPISAS.exceptions import ServerNotReachable, IncompleteJSONSchema

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


def get_response_for_get_request(url):
    try:
        logging.info("GET request to " + str(url))
        response = requests.get(url)
        return response
    except requests.exceptions.ConnectionError as e:
        logging.error(e)
        logging.error("Please check that the server is reachable and retry.")
        raise ServerNotReachable


def validate_schema(json_instance, json_schema):
    try:
        incomplete_warning_message = "No complete JSON Schema provided for validation"
        if json_schema and "type" in json_schema and "properties" in json_schema:
            json_instance_keys = sorted(json_instance.keys())
            json_schema_keys = sorted(json_schema["properties"].keys())
            if json_instance_keys == json_schema_keys:
                jsonschema.validate(json_instance, json_schema)
                logging.info("JSON object validated by JSON Schema")
            else:
                logging.error(incomplete_warning_message + " Keys misaligned")
                raise IncompleteJSONSchema
        else:
            logging.error(incomplete_warning_message + " Type and Properties absent")
            raise IncompleteJSONSchema
    except jsonschema.exceptions.ValidationError as error:
        logging.error(f"ValidationError in validating JSON object with JSON Schema: {error}")
        raise
    except jsonschema.exceptions.SchemaError as error:
        logging.error(f"SchemaError in validating JSON object with JSON Schema: {error}")
        raise

