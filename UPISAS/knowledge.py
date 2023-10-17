from dataclasses import dataclass


@dataclass
class Knowledge:
    monitored_data: dict
    analysis_data: dict
    execute_data: dict
