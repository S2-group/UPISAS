from UPISAS.strategies.swim_reactive_strategy import ReactiveAdaptationManager
from UPISAS.exemplar import Exemplar
from UPISAS.exemplars.swim import SWIM
import signal
import sys
import time

if __name__ == '__main__':
    
    exemplar = SWIM(auto_start=True)
    time.sleep(3)
    exemplar.start_run()
    time.sleep(3)

    try:
        strategy = ReactiveAdaptationManager(exemplar)

        strategy.get_monitor_schema()
        strategy.get_adaptation_options_schema()
        strategy.get_execute_schema()

        while True:
            input("Try to adapt?")
            strategy.monitor(verbose=True)
            if strategy.analyze():
                if strategy.plan():
                    strategy.execute()
            
    except (Exception, KeyboardInterrupt) as e:
        exit_code = 0
        if (isinstance(e, Exception)):
          # Exception occurred
          print("\nSomething went wrong: {e}")
          exit_code = 1

        print("\nQuiting UPISAS, waiting for container to terminate...")
        exemplar.stop_container()
        sys.exit(exit_code)