from Strategy import Strategy


class ExampleStrategy(Strategy):

    def analyze(self):
        data = self.knowledge.monitored_data
        mean_i1 = sum(data["i1"])/len(data["i1"])
        print("[Analysis]\tmean_x1: " + str(mean_i1))
        if mean_i1 > 0.05:
            self.knowledge.analysis_data["mean_i1"] = mean_i1
            return True
        return False

    def plan(self):
        data = self.knowledge.analysis_data["mean_i1"]
        if data > 0.5:
            self.knowledge.execute_data = {"o1": 2, "o2": 5}
            return True
        return False
