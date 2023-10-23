from dataclasses import dataclass


@dataclass
class Knowledge:
    monitored_data: dict
    analysis_data: dict
    plan_data: dict

    adaptations_options: dict

    monitor_schema: dict
    execute_schema: dict
    adaptations_options_schema: dict
