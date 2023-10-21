from UPISAS.example_strategy import ExampleStrategy
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
    #     strategy = ExampleStrategy(exemplar)

    #     while True:
    #         input()
    #         strategy.monitor()
    #         if strategy.analyze():
    #             if strategy.plan():
    #                 strategy.execute(strategy.knowledge.plan_data)
    # except:
    #     exemplar.stop()
    #     sys.exit(0)