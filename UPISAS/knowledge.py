from dataclasses import dataclass


@dataclass
class Knowledge:
    monitored_data: dict
    analysis_data: dict
    plan_data: dict

    adaptation_options: dict

    monitor_schema: dict
    execute_schema: dict
    adaptation_options_schema: dict
