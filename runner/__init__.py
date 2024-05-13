import sys
import traceback
import dill as pickle
import hashlib
import ast
from typing import List
from importlib import util
import multiprocessing
from os import environ

from .ConfigValidator.Config.Validation import ConfigValidator
from .ConfigValidator.CLIRegister import CLIRegister
from .ConfigValidator.Config.Models import Metadata
from .ConfigValidator.CustomErrors import BaseError, ConfigInvalidClassNameError
from .ExperimentOrchestrator.Experiment.ExperimentController import ExperimentController

def is_no_argument_given(args: List[str]): return (len(args) == 1)
def is_config_file_given(args: List[str]): return (args[1][-3:] == '.py')
def load_and_get_config_file_as_module(filepath: str):
    module_name = filepath.split('/')[-1].replace('.py', '')
    spec = util.spec_from_file_location(module_name, filepath) 
    config_file = util.module_from_spec(spec)
    sys.modules[module_name] = config_file
    spec.loader.exec_module(config_file)
    return config_file

def calc_ast_md5sum(src, name):
    tree = compile(src, name, 'exec', flags=ast.PyCF_ONLY_AST, optimize=0)

    for node in ast.walk(tree):
        # Ignores empty lines and comment only lines
        if hasattr(node, 'lineno'):
            setattr(node, 'lineno', 0)
        if hasattr(node, 'col_offset'):
            setattr(node, 'col_offset', 0)
        if hasattr(node, 'end_lineno'):
            setattr(node, 'end_lineno', 0)
        if hasattr(node, 'end_col_offset'):
            setattr(node, 'end_col_offset', 0)

        # Ignore docstring
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.ClassDef, ast.Module)) and ast.get_docstring(node) is not None:
            docstring_node = node.body[0].value
            if isinstance(docstring_node, ast.Str):
                docstring_node.s = ''
            elif isinstance(docstring_node, ast.Constant) and isinstance(docstring_node.value, str):
                docstring_node.value = ''

    return hashlib.md5(pickle.dumps(tree)).digest()


def handle_command():
    """
    This method is called from the command line.
    Runs can be executed either via the command line through this method,
    or through code directly by using the `run_experiment` method.
    """
    try: 
        if is_no_argument_given(sys.argv):
            sys.argv.append('help')
            CLIRegister.parse_command(sys.argv)
        elif is_config_file_given(sys.argv):                                # If the first argument ends with .py -> a config file is entered
            run_experiment(sys.argv[1])
        else:                                                               # Else, a utility command is entered
            CLIRegister.parse_command(sys.argv)
    except BaseError as e:                                                  # All custom errors are displayed in custom format
        print(f"\n{e}")
        sys.exit(1)
    except:                                                                 # All non-covered errors are displayed normally
        traceback.print_exc()
        sys.exit(1)



def run_experiment(filepath: str, name=None):
    """
    args input is either sys.argv in the case of command-line execution,
    or else an array of strings in the same format. e.g. 
    Cmd line -> ['experiments.py', 'path/to/RunnerConfig.py']
    From code -> ['path/to/RunnerConfig.py']
    """
    multiprocessing.set_start_method('fork')                        # Set "fork" as the default method for spawning new processes 
                                                                            # (in this way the new processes will have a shared context when running)                   
    config_file = load_and_get_config_file_as_module(filepath)

    if name is not None:
        environ["EXPERIMENT_NAME"] = name
    else:
        del environ["EXPERIMENT_NAME"] # unset and use default value in RunnerConfig.py

    if hasattr(config_file, 'RunnerConfig'):
        config = config_file.RunnerConfig()                         # Instantiate config from injected file
        metadata = Metadata(
            calc_ast_md5sum(pickle.source.getsource(config_file), filepath)  # hash of the whole file, not just RunnerConfig
        )

        ConfigValidator.validate_config(config)                     # Validate config as a valid RunnerConfig
        ExperimentController(config, metadata).do_experiment()      # Instantiate controller with config and start experiment
    else:
        raise ConfigInvalidClassNameError
