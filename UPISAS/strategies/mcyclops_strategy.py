from UPISAS.strategy import Strategy
import requests


class MLOpsStrategy(Strategy):
    window = {} # Enables saving of last window_size data points for analysis
    window_size = 20 # number of data points to consider for analysis
    last_known_data_hash = ""
    last_known_accuracy = 0.0
    last_known_version = ""
    threshold = 0.03 # minimum change in accuracy to trigger retraining
    should_adapt = False
    requested_adaptation = False
    wait_time = 2 # seconds to wait between monitoring. When we retrain the model
                    # temporarily set this higher to avoid overloading the system

    def prepare_data(self):
        data = self.knowledge.monitored_data
        self.last_known_accuracy = data['accuracy'][-1]

        if self.last_known_data_hash == "":
            self.last_known_data_hash = data['data_hash'][-1]

        if data['model_version'] != self.last_known_version:
            self.last_known_version = data['model_version']
            self.wait_time = 2

    def verify_minimum_data(self):
        # if we have less than the window size, we can't analyze yet. Append 0 accuracy
        if len(self.knowledge.monitored_data['accuracy']) < self.window_size:
            if 'model_acc' not in self.knowledge.monitored_data:
                self.update_knoweldge('model_acc', [])
            if len(self.knowledge.monitored_data['model_acc']) < self.window_size:
                self.knowledge.monitored_data['model_acc'].append(0.0)
            print("[Monitor]\tNot enough data to analyze.")
            self.should_adapt = False
        # if we have enough data, we can analyze
        else:
            self._get_accuracy_count()
            self.should_adapt = True

    def update_window(self):
        # reset the window for the current iteration to the last window_size data points
        if len(self.knowledge.monitored_data['accuracy']) >= self.window_size:
            for key in list(self.knowledge.monitored_data.keys()):
                self.window[key] = self.knowledge.monitored_data[key][-self.window_size:]
                
            print("[Monitor]\ttrimmed data to window size.")

    def analyze(self):
        self.prepare_data()

        self.verify_minimum_data()

        self.update_window()

        accuracy = self.window['model_acc'][-1]

        # if accuracy has decreased by more than the threshold, retrain
        if accuracy < self.last_known_accuracy - self.threshold:
            self.knowledge.adaptation_options['retrain'] = True
            print("[Analyze]\tRetraining required.")
            return True
        
        print("[Analyze]\tNo retraining required.")
        return False

    def plan(self):
        
        if self.last_known_data_hash != self.knowledge.monitored_data['data_hash'][-1]:
            self.knowledge.plan_data['retrain'] = True
            self.knowledge.plan_data['ngram'] = 1
            self.knowledge.plan_data['data_path'] = './mlops/data/emails.csv'
            print("[Plan]\tData has changed, model can be retrained.")
            self.last_known_data_hash = self.knowledge.monitored_data['data_hash'][-1]
            return True
        
        # if self.knowledge.adaptation_options['retrain']:
            # self.knowledge.adaptation_options['ngram'] += 1
            # print("[Plan]\tIncreased ngram to: " + str(self.knowledge.adaptation_options['ngram']))
            # return True
        
        return False
    
    def get_should_adapt(self):
        return self.should_adapt
    
    def get_requested_adaptation(self):
        return self.requested_adaptation
    
    def get_all_data(self):
        # Convert monitored_data into an array of dicts and return
        return_data = []
        for i in range(len(self.knowledge.monitored_data['accuracy'])):
            data = {}
            for key in list(self.knowledge.monitored_data.keys()):
                data[key] = self.knowledge.monitored_data[key][i]
            return_data.append(data)
        return return_data
    
    def _get_accuracy_count(self):
        data = self.knowledge.monitored_data
        counter = 0
        for i in range(self.window_size):
            if data['prediction'][i] == data['actual_label'][i]:
                counter += 1
        
        accuracy = counter / self.window_size
        print(f"[Monitor]\tAccuracy: {accuracy}")
        self.knowledge.monitored_data['model_acc'].append(accuracy)
