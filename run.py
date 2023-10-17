from UPISAS.ExampleStrategy import ExampleStrategy
from UPISAS.Exemplar import Exemplar

if __name__ == '__main__':
    exemplar = Exemplar("http://localhost:3000", "gabrielmoreno/swim", "swim", auto_start=True)
    strategy = ExampleStrategy(exemplar)

    while True:
        input()
        strategy.monitor()
        if strategy.analyze():
            if strategy.plan():
                strategy.execute(strategy.knowledge.plan_data)
