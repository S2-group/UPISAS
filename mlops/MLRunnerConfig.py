from runner.EventManager.RunnerEvents import RunnerEvents
from runner.EventManager.EventSubscriptionController import EventSubscriptionController
from runner.ConfigValidator.Config.Models import (
  RunTableModel, StrategyModel, RunnerContext, OperationType
)
from runner.ExtendedTyping.Typing import SupportsStr
from runner.ProgressManager.Output.OutputProcedure import OutputProcedure as output

import pandas as pd

from typing import Dict, List, Any, Optional
from pathlib import Path
from os.path import dirname, realpath
from os import getenv
import threading
import time
import requests

from UPISAS.strategies.mlops_strategy import MLOpsStrategy
from UPISAS.exemplars.mlops_exemplar import MlopsExemplar


return_data = []
monitor_lock = threading.Lock()


def send_inference_requests(**kwargs):
    strategy = kwargs['strategy']
    duration = 2
    e1_df = pd.read_csv('./mlops/data/enron1.csv')
    e2_df = pd.read_csv('./mlops/data/enron2.csv')
    df = e1_df
    counter = 0
    while True:
        if counter == 60:
            # switch to the second dataset to force a drift in data
            df = e2_df

        if counter == 70:
            requests.post("http://localhost:5001/update", json={})

        if counter >= 140:
            break

        # randomly pick an email from the dataset
        email = df.sample(n=200, random_state=42).iloc[counter].to_dict()
        
        with monitor_lock:
            strategy.monitor(email)
            duration = strategy.wait_time

        counter += 1
        time.sleep(duration)


class RunnerConfig:
    """
    This test executes as follows:
    1. A model for the emails is trained and saved on Enron1 emails before the experiment starts.
    2. The experiment starts and the model is loaded by all 4 gunicorn workers.
    3. Every 5 seconds, the model is sent a request with a new email to classify.
    4. After 60 requests, the email requests are pulled from the Enron2 dataset to force a drift in the data.
    5. After 70 requests, the training data is updated with the new Enron2 data, causing the monitor method to return a new data hash.
    6. The model is retrained.
    7. The experiment ends after 140 requests.

    The effects of the above will differ based on the value of the "retrain" adaptation option, this way we get output data for both settings.
    """

    ROOT_DIR = Path(dirname(realpath(__file__)))

    # ================================ USER SPECIFIC CONFIG ================================
    """The name of the experiment."""
    name:                       str             = getenv("EXPERIMENT_NAME", "your_experiment_name")

    """The path in which Experiment Runner will create a folder with the name `self.name`, in order to store the
    results from this experiment. (Path does not need to exist - it will be created if necessary.)
    Output path defaults to the config file's path, inside the folder 'experiments'"""
    results_output_path:        Path            = ROOT_DIR / 'experiments'

    """Experiment operation type. Unless you manually want to initiate each run, use `OperationType.AUTO`."""
    operation_type:             OperationType   = OperationType.AUTO

    """The time Experiment Runner will wait after a run completes.
    This can be essential to accommodate for cooldown periods on some systems."""
    time_between_runs_in_ms:    int             = 1000

    exemplar = None
    strategy = None

    # Dynamic configurations can be one-time satisfied here before the program takes the config as-is
    # e.g. Setting some variable based on some criteria
    def __init__(self):
        """Executes immediately after program start, on config load"""

        EventSubscriptionController.subscribe_to_multiple_events([
            (RunnerEvents.BEFORE_EXPERIMENT, self.before_experiment),
            (RunnerEvents.BEFORE_RUN       , self.before_run       ),
            (RunnerEvents.START_RUN        , self.start_run        ),
            (RunnerEvents.START_MEASUREMENT, self.start_measurement),
            (RunnerEvents.INTERACT         , self.interact         ),
            (RunnerEvents.STOP_MEASUREMENT , self.stop_measurement ),
            (RunnerEvents.STOP_RUN         , self.stop_run         ),
            (RunnerEvents.POPULATE_RUN_DATA, self.populate_run_data),
            (RunnerEvents.AFTER_EXPERIMENT , self.after_experiment )
        ])
        self.run_table_model = None  # Initialized later

        output.console_log("Custom config loaded")

    def create_run_table_model(self) -> RunTableModel:
        """Create and return the run_table model here. A run_table is a List (rows) of tuples (columns),
        representing each run performed"""
        retrain = StrategyModel("retrain", [False, True])
        self.run_table_model = RunTableModel(
            strategies=[retrain],
            exclude_variations=[
            ],
            data_columns=['model_version', 'prediction', 'confidence', 'model_acc', 'actual_label', 'window_acc']
        )
        return self.run_table_model

    def before_experiment(self) -> None:
        """Perform any activity required before starting the experiment here
        Invoked only once during the lifetime of the program."""

        output.console_log("Config.before_experiment() called!")

    def before_run(self) -> None:
        """Perform any activity required before starting a run.
        No context is available here as the run is not yet active (BEFORE RUN)"""

        self.exemplar = MlopsExemplar(auto_start=True)
        self.strategy = MLOpsStrategy(self.exemplar)

        self.exemplar.start_run()

        output.console_log("Config.before_run() called!")

    def start_run(self, context: RunnerContext) -> None:
        """Perform any activity required for starting the run here.
        For example, starting the target system to measure.
        Activities after starting the run should also be performed here."""

        self.exemplar.wait_for_server()
        self.exemplar.reset_email_data()
        self.exemplar.prepare_model()
        self.exemplar.pretrain_model()

        output.console_log("Config.start_run() called!")

    def start_measurement(self, context: RunnerContext) -> None:
        """Perform any activity required for starting measurements."""


        output.console_log("Config.start_measurement() called!")

    def interact(self, context: RunnerContext) -> None:
        """Perform any interaction with the running target system here, or block here until the target finishes."""

        did_update_data = False

        self.strategy.get_monitor_schema()
        self.strategy.get_adaptation_options_schema()
        self.strategy.get_execute_schema()

        thread = threading.Thread(target=send_inference_requests, kwargs={'strategy': self.strategy})
        thread.daemon = True
        thread.start()

        while thread.is_alive():
            with monitor_lock:
                # If we have enough data, and did not already request an update, analyze it
                if self.strategy.get_should_adapt():
                    print("[Interact]\tAnalyzing data.")
                    if self.strategy.analyze():
                        # Depending on the run, we may want to retrain the model
                        if not did_update_data:
                            self.exemplar.update_email_data()
                            did_update_data = True

                        should_execute = (self.strategy.plan()
                            and bool(context.run_variation['retrain'])
                            and not self.strategy.get_requested_adaptation())
                        
                        if should_execute:
                            self.strategy.wait_time = 20
                            self.strategy.execute(self.strategy.knowledge.plan_data)
                            self.strategy.requested_adaptation = True

            time.sleep(4.5)

        output.console_log("Config.interact() called!")

    def stop_measurement(self, context: RunnerContext) -> None:
        """Perform any activity here required for stopping measurements."""

        for i in range(len(self.strategy.all_data)):
            self.strategy.all_data[i]['retrain'] = context.run_variation['retrain']

        return_data.append(self.strategy.all_data)

        output.console_log("Config.stop_measurement called!")

    def stop_run(self, context: RunnerContext) -> None:
        """Perform any activity here required for stopping the run.
        Activities after stopping the run should also be performed here."""

        self.exemplar.stop_run()

        output.console_log("Config.stop_run() called!")

    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, SupportsStr]]:
        """Parse and process any measurement data here.
        You can also store the raw measurement data under `context.run_dir`
        Returns a dictionary with keys `self.run_table_model.data_columns` and their values populated"""

        for run_data in return_data:
            results_df = pd.DataFrame(run_data)
            results_df.to_csv(context.run_dir / 'results.csv', index=False)

        output.console_log("Config.populate_run_data() called!")
        return None

    def after_experiment(self) -> None:
        """Perform any activity required after stopping the experiment here
        Invoked only once during the lifetime of the program."""

        output.console_log("Config.after_experiment() called!")

    # ================================ DO NOT ALTER BELOW THIS LINE ================================
    experiment_path:            Path             = None
