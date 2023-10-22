from dataclasses import dataclass


@dataclass
class Knowledge:
    monitored_data: dict
    analysis_data: dict
    plan_data: dict
    possible_adaptations_values: dict
    monitor_schema: dict
    execute_schema: dict
    possible_adaptations_schema: dict
