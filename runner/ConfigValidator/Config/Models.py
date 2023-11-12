from enum import Enum, auto
import itertools
from pathlib import Path
import random
from typing import Dict, List, Tuple

from runner.ConfigValidator.CustomErrors import BaseError
from runner.ExtendedTyping.Typing import SupportsStr
from runner.ProgressManager.RunTable.Models.RunProgress import RunProgress


class RunnerContext:

    def __init__(self, run_variation: dict, run_nr: int, run_dir: Path):
        self.run_variation = run_variation
        self.run_nr = run_nr
        self.run_dir = run_dir


class StrategyModel:
    def __init__(self, strategy_name: str, parameter_values: List[SupportsStr]):
        if len(set(parameter_values)) != len(parameter_values):
            raise BaseError(f"Treatment levels for factor {strategy_name} are not unique!")

        self.__strategy_name = strategy_name
        self.__parameter_values = parameter_values

    @property
    def strategy_name(self) -> str:
        return self.__strategy_name

    @property
    def parameter_values(self) -> List[SupportsStr]:
        return self.__parameter_values
    

class FactorModel:
    def __init__(self, factor_name: str, treatments: List[SupportsStr]):
        if len(set(treatments)) != len(treatments):
            raise BaseError(f"Treatment levels for factor {factor_name} are not unique!")

        self.__factor_name = factor_name
        self.__treatments = treatments

    @property
    def factor_name(self) -> str:
        return self.__factor_name

    @property
    def treatments(self) -> List[SupportsStr]:
        return self.__treatments


class RunTableModel:
    def __init__(self,
                 strategies: List[StrategyModel],
                 exclude_variations: List[Dict[StrategyModel, List[SupportsStr]]] = None,
                 data_columns: List[str] = None,
                 shuffle: bool = False
                 ):
        if exclude_variations is None:
            exclude_variations = {}
        if data_columns is None:
            data_columns = []

        if len(set([factor.factor_name for factor in strategies])) != len(strategies):
            raise BaseError("Duplicate factor name detected!")

        if len(set(data_columns)) != len(data_columns):
            raise BaseError("Duplicate data column detected!")

        # We've renamed factors to models at the top level.
        # No need to touch the following yet.
        self.__factors = strategies
        self.__exclude_variations = exclude_variations
        self.__data_columns = data_columns
        self.__shuffle = shuffle

    def get_factors(self) -> List[StrategyModel]:
        return self.__factors

    def get_data_columns(self) -> List[str]:
        return self.__data_columns

    def generate_experiment_run_table(self) -> List[Dict]:
        def __filter_list(full_list: List[Tuple]):
            if len(self.__exclude_variations) == 0:
                return full_list

            to_remove_indices = []
            for exclusion in self.__exclude_variations:
                # Construct the exclusion tuples
                list_of_lists = []
                indexes = []
                for factor, treatment_list in exclusion.items():
                    list_of_lists.append(treatment_list)
                    indexes.append(self.__factors.index(factor))
                exclude_combinations_list = list(itertools.product(*list_of_lists))

                # Mark the exclusions in the full table
                for idx, elem in enumerate(full_list):
                    for exclude_combo in exclude_combinations_list:
                        if all([exclude_combo[i] == elem[indexes[i]] for i in range(len(indexes))]):
                            to_remove_indices.append(idx)

            to_remove_indices.sort(reverse=True)
            for idx in to_remove_indices:
                del full_list[idx]
            return full_list

        list_of_lists = [factor.treatments for factor in self.__factors]
        combinations_list = list(itertools.product(*list_of_lists))
        filtered_list = __filter_list(combinations_list)

        column_names = ['__run_id', '__done']  # Needed for experiment-runner functionality
        for factor in self.__factors:
            column_names.append(factor.factor_name)

        if self.__data_columns:
            for data_column in self.__data_columns:
                column_names.append(data_column)

        experiment_run_table = []
        for i, combo in enumerate(filtered_list):
            row_list = list(combo)
            row_list.insert(0, f'run_{i}')  # __run_id
            row_list.insert(1, RunProgress.TODO)  # __done

            if self.__data_columns:
                for _ in self.__data_columns:
                    row_list.append(" ")
            experiment_run_table.append(dict(zip(column_names, row_list)))

        if self.__shuffle:
            random.shuffle(experiment_run_table)
        return experiment_run_table
    

class Metadata:

    def __init__(self, md5sum: bytes):
        self._md5sum = md5sum

    @property
    def md5sum(self):
        return self._md5sum

    @md5sum.setter
    def md5sum(self, md5sum: bytes):
        self._md5sum = md5sum


class OperationType(Enum):
    """If set to AUTO, an experiment will continue with the next run (after waiting `RunnerConfig.time_between_runs_in_ms` milliseconds)
    automatically without waiting for any other stimuli."""
    AUTO = auto()

    """If set to SEMI, an experiment will continue with the next run (after waiting `RunnerConfig.time_between_runs_in_ms` milliseconds),
    only if the callback for the event `RunnerEvents.CONTINUE` has returned."""
    SEMI = auto()


