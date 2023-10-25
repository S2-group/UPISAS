from UPISAS.strategy import Strategy


class EmptyStrategy(Strategy):

    def analyze(self):
        return True

    def plan(self):
        return True
