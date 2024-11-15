from runner.ExperimentOrchestrator.Misc.BashHeaders import BashHeaders

class BaseError(Exception):
    def __init__(self, message):
        super().__init__(BashHeaders.FAIL + '[FAIL]: ' + BashHeaders.ENDC + 
            'EXPERIMENT_RUNNER ENCOUNTERED AN ERROR!\n\n' + BashHeaders.FAIL + message + BashHeaders.ENDC)
        

class CommandNotRecognisedError(BaseError):
    def __init__(self):
        super().__init__("The command entered by the user is not recognised")


class InvalidUserSpecifiedPathError(BaseError):
    def __init__(self, path):
        super().__init__("The user specified path is invalid or the user does not have the correct permissions" +
                        f"\n{path}")


class InvalidConfigTypeSpecifiedError(BaseError):
    def __init__(self):
        super().__init__("The specified config type did not match.")


class ConfigBaseError(BaseError):
    def __init__(self, text: str):
        super().__init__(text)


class ConfigInvalidError(ConfigBaseError):
    def __init__(self):
        super().__init__("Config found to be invalid, please refer to the config attribute table.")


class ConfigInvalidClassNameError(ConfigBaseError):
    def __init__(self):
        super().__init__("The config file specified does not have a valid config class name as expected (RunnerConfig).")


class ConfigAttributeInvalidError(ConfigBaseError):
    def __init__(self, attribute_in_question, found, expected):
        super().__init__("INVALID config attribute " + 
                            BashHeaders.UNDERLINE + attribute_in_question + BashHeaders.ENDC + BashHeaders.FAIL + "\n" +
                            "%-*s  %s\n" % (10, "FOUND:", found) +
                            "%-*s  %s" % (10, "EXPECTED:", expected) + BashHeaders.ENDC)
        

class ExperimentOutputFileDoesNotExistError(BaseError):
    def __init__(self):
        super().__init__("The " + BashHeaders.UNDERLINE + "experiment_path" + BashHeaders.ENDC + BashHeaders.FAIL + 
                            " (experiment output folder) exists, but the " + 
                            BashHeaders.UNDERLINE + "run_table.csv" + BashHeaders.ENDC + BashHeaders.FAIL +
                            " does not exist.\n" +
                            "Experiment-runner cannot restart!")
        

class ProgressBaseError(BaseError):
    def __init__(self, text: str):
        super().__init__(text)


class AllRunsCompletedOnRestartError(ProgressBaseError):
    def __init__(self):
        super().__init__("The experiment was restarted, but all runs are already completed.")