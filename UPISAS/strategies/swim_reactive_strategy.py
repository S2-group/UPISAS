from UPISAS.strategy import Strategy

#This is a port of the ReactiveAdaptationManager originally published alongside SWIM.
class ReactiveAdaptationManager(Strategy):
    #These three come from the swim.ini file.
    RT_THRESHOLD = 0.75
    DIMMER_MARGIN = 0.1
    BROWNOUT_LEVELS = 5
    MAX_SERVICE_RATE = 1 / 0.04452713

    def analyze(self):
        data = self.knowledge.monitored_data
        print(data)
        self.knowledge.analysis_data["server_booting"] = data["servers"] > data["active_servers"]
        
        self.knowledge.analysis_data["spare_utilization"] = sum([server["utilization_value"] for server in data["utilization"][-1]])
        self.knowledge.analysis_data["rt_sufficient"] = False
        self.knowledge.analysis_data["dimmer_at_min"] = data["dimmer_factor"][-1] < self.DIMMER_MARGIN
        self.knowledge.analysis_data["dimmer_at_max"] = data["dimmer_factor"][-1] > (1.0 - self.DIMMER_MARGIN) #I could use the dimer_margin, but I don't trust C++ floats.
        self.knowledge.analysis_data["is_server_removable"] = data["servers"][-1] > 1
        self.knowledge.analysis_data["server_room"] = data["servers"][-1] < data["max_servers"][-1]
        self.knowledge.analysis_data["current_dimmer"] = data["dimmer_factor"][-1]
        self.knowledge.analysis_data["current_servers"] = data["servers"][-1]
        if(data["basic_rt"][-1] > self.RT_THRESHOLD):
            return True
        elif(data["basic_rt"][-1] < self.RT_THRESHOLD):

            self.knowledge.analysis_data["rt_sufficient"] = True
            return True
        
        return False



    def plan(self):
        if((self.knowledge.analysis_data["rt_sufficient"])):
            if(self.knowledge.analysis_data["spare_utilization"] > 1):
                if(not(self.knowledge.analysis_data["dimmer_at_max"])):
                    self.knowledge.plan_data["dimmer_factor"] = self.knowledge.analysis_data["current_dimmer"] + self.DIMMER_MARGIN
                    self.knowledge.plan_data["server_number"] = self.knowledge.analysis_data["current_servers"] #This is due to the schema validation checking for keys.
                    return True
                elif(not(self.knowledge.analysis_data["server_booting"]) and self.knowledge.analysis_data["is_server_removable"]):
                    self.knowledge.plan_data["server_number"] = self.knowledge.analysis_data["current_servers"] - 1
                    self.knowledge.plan_data["dimmer_factor"] = self.knowledge.analysis_data["current_dimmer"]
                    return True

        else:
            self.knowledge.analysis_data["dimmer_at_min"]
            if(not(self.knowledge.analysis_data["server_booting"]) and (self.knowledge.analysis_data["server_room"])):
                self.knowledge.plan_data["server_number"] = self.knowledge.analysis_data["current_servers"] + 1
                self.knowledge.plan_data["dimmer_factor"] = self.knowledge.analysis_data["current_dimmer"]
                return True
            elif(not(self.knowledge.analysis_data["dimmer_at_min"])):
                self.knowledge.plan_data["dimmer_factor"] = self.knowledge.analysis_data["current_dimmer"] - self.DIMMER_MARGIN
                self.knowledge.plan_data["server_number"] = self.knowledge.analysis_data["current_servers"]
                return True
            
        return False