from UPISAS.goal_managers.demo_manager import DemoGoalManagement
from UPISAS.strategies.demo_strategy import DemoStrategy
from UPISAS.exemplar import Exemplar
from UPISAS.exemplars.swim import SWIM
import signal
import sys


# def signal_handler(sig, frame):
#     print('You pressed Ctrl+C!')
#     exemplar.stop()
#     sys.exit(0)

# signal.signal(signal.SIGINT, signal_handler)
if __name__ == '__main__':
    
    exemplar = SWIM(auto_start=True)
    exemplar.start_run()
    # try:
    #     goal_manager = DemoGoalManagement(exemplar, ["adapt"], DemoStrategy)
    #     exemplar.add_goal_manager(goal_manager)

    #     while True:
    #         execute = False
    #         input()
    #         exemplar.monitor()
    #         strategies = goal_manager.get_strategies({"errors": [], "state": ""})
    #         for strategy in strategies:
    #             if strategy.analyze():
    #                 if strategy.plan():
    #                     execute = True

    #         if execute:
    #             conflicts = exemplar.check_for_update_conflicts()
    #             if conflicts:
    #                 goal_manager.resolve_conflicts(conflicts)
    #             exemplar.execute(exemplar.knowledge.plan_data)
    # except:
    #     exemplar.stop()
    #     sys.exit(0)