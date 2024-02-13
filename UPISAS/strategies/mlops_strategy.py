from UPISAS.strategy import Strategy
import requests


class MLOpsStrategy(Strategy):
    all_data = [] # Enables saving of all data points for analysis
    window_size = 20 # number of data points to consider for analysis
    last_known_data_hash = ""
    last_known_accuracy = 0.0
    last_known_version = ""
    threshold = 0.03 # minimum change in accuracy to trigger retraining
    should_adapt = False
    requested_adaptation = False
    wait_time = 2 # seconds to wait between monitoring. When we retrain the model
                    # temporarily set this higher to avoid overloading the system
    
    def monitor(self, email):
        # We store the data on the managing system side to avoid needing to use redis
        response = requests.post(f'{self.exemplar.base_endpoint}/monitor', json=email)
        data = response.json()
        print(data)

        self.all_data.append(data)

        self.last_known_accuracy = data['accuracy']

        if self.last_known_data_hash == "":
            self.last_known_data_hash = data['data_hash']

        if data['model_version'] != self.last_known_version:
            self.last_known_version = data['model_version']
            self.wait_time = 2
            # self.requested_adaptation = False # reset the flag so we know the model has been updated

        for key in list(data.keys()):
            if key not in self.knowledge.monitored_data:
                self.knowledge.monitored_data[key] = []
            self.knowledge.monitored_data[key].append(data[key])
        print("[Knowledge]\tdata monitored so far: " + str(self.knowledge.monitored_data))

        if len(self.knowledge.monitored_data['accuracy']) < self.window_size:
            if 'model_acc' not in self.knowledge.monitored_data:
                self.knowledge.monitored_data['model_acc'] = []
            if len(self.knowledge.monitored_data['model_acc']) < self.window_size:
                self.knowledge.monitored_data['model_acc'].append(0.0)
            print("[Monitor]\tNot enough data to analyze.")
            self.should_adapt = False
        else:
            self._get_accuracy_count()
            self.should_adapt = True

        for key in list(self.knowledge.monitored_data.keys()):
            if len(self.knowledge.monitored_data[key]) > self.window_size:
                self.knowledge.monitored_data[key].pop(0)
        print("[Monitor]\ttrimmed data to window size.")

    def analyze(self):
        accuracy = self.all_data[-1]['model_acc']

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
    
    def _get_accuracy_count(self):
        data = self.knowledge.monitored_data
        counter = 0
        for i in range(self.window_size):
            if data['prediction'][i] == data['actual_label'][i]:
                counter += 1
        
        accuracy = counter / self.window_size
        print(f"[Monitor]\tAccuracy: {accuracy}")
        self.knowledge.monitored_data['model_acc'].append(accuracy)
        self.all_data[-1]['model_acc'] = accuracy
