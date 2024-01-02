import os
import uuid
import inspect
from typing import List
from shutil import copyfile
from tabulate import tabulate

from ..Config import RunnerConfig
from ...ExperimentOrchestrator import BashHeaders
from ...ExperimentOrchestrator import is_path_exists_or_creatable_portable
from ...ProgressManager import OutputProcedure as output
from ..CustomErrors.CLIErrors import *

class ConfigCreate:
    @staticmethod
    def description_params() -> str:
        return "[path_to_user_specified_dir]"

    @staticmethod
    def description_short() -> str:
        return "Creates a config file in the `experiments', or user-specified, directory"

    @staticmethod
    def description_long() -> str:
        output.console_log_bold("... TODO give usage instructons ...")

    @staticmethod
    def execute(args=None) -> None:
        try:
            destination = ""
            if args is None:
                filepath = __file__.split('/')
                filepath.pop()
                filepath = '/'.join(filepath) + "/../../../examples/"
                destination = os.path.abspath(filepath)
            else:
                if len(args) == 3:
                    destination = args[2]
                else:
                    raise CommandNotRecognisedError
        except:
            raise CommandNotRecognisedError

        if destination[-1] != "/":
            destination += "/"

        if not is_path_exists_or_creatable_portable(destination):
            raise InvalidUserSpecifiedPathError(destination)
        
        module = RunnerConfig
        src = inspect.getmodule(module).__file__
        dest_folder = destination
        #destination += src.split('/')[-1]
        config_unique_name = 'RunnerConfig-' + str(uuid.uuid1()) + '.py'
        # config_unique_name = 'RunnerConfig-' + 'foobar' + '.py' # FIXME: DEBUG ONLY BUILDS
        destination += config_unique_name
        copyfile(src, destination)
        output.console_log_OK(
            f"Successfully created new config with unique identifier in: {dest_folder}" +
            f"\nWith the unique name (please rename): {config_unique_name}"
        )

class Prepare:
    @staticmethod
    def description_params() -> str:
        return ""

    @staticmethod
    def description_short() -> str:
        return "(WIP) Prepare system -- Install all dependencies"

    @staticmethod
    def description_long() -> str:
        output.console_log_bold("Prepare will install all the user's required dependencies to be able to run experiment-runner on their system.")

    @staticmethod
    def execute(args=None) -> None:
        pass

class Help:
    @staticmethod
    def description_params() -> str:
        return ""

    @staticmethod
    def description_short() -> str:
        return "An overview of all available commands"

    @staticmethod
    def description_long() -> str:
        print(BashHeaders.BOLD + "--- EXPERIMENT_RUNNER HELP ---" + BashHeaders.ENDC)
        print("\n%-*s  %s" % (10, "Usage:", "python experiment-runner/ <path_to_config.py>"))
        print("%-*s  %s" % (10, "Utility:", "python experiment-runner/ <command>"))

        print("\nAvailable commands:\n")
        print(tabulate([(k, v.description_params()) for k, v in CLIRegister.register.items()], ["Command", "Parameters"]))

        print("\nHelp can be called for each command:")
        print(BashHeaders.WARNING + "example: " + BashHeaders.ENDC + "python experiment-runner/ prepare help")

    @staticmethod
    def execute(args=None) -> None:
        Help.description_long()

class CLIRegister:
    register = {
        "config-create":    ConfigCreate,
        "prepare":          Prepare,
        "help":             Help
    }

    @staticmethod 
    def parse_command(args: List):
        try:
            command_class = CLIRegister.register.get(args[1])
        except:
            raise CommandNotRecognisedError

        if len(args) == 2:
            command_class.execute()
        elif len(args) > 2:
            if args[2] == 'help':
                command_class.description_long()
            else:
                command_class.execute(args)