from experiment.components import BaseComponent

def default_summary_function(self):
    n_trials = len(self.records)
    self.summary = {'n_trials': n_trials}

class DataStore(BaseComponent):
    COMPONENT_TYPE = "datastore"
    def __init__(self, summary_function=None):
        if summary_function is None:
            self.summary_function = default_summary_function
        else:
            self.summary_function = summary_function
        self.summary = {}
        self.key_is_scalar = {}
        self.records = {}
        self.trialid = 0

    def record(self, **kwargs):
        for k, v in kwargs.items():
            key_state = self.key_is_scalar.get(k)
            if key_state is None:
                self.current_trial_record[k] = v
                self.key_is_scalar[k] = True
            elif key_state:
                self.current_trial_record[k] = [self.current_trial_record[k], v]
            else:
                self.current_trial_record[k].append(v)

    @property
    def current_trial_record(self):
        if self.trialid not in self.records:
            self.records[self.trialid] = {"trialid": self.trialid}
        return self.records[self.trialid]

    def flush(self):
        raise NotImplementedError("Flush method must be implemented by subclasses")

    def close(self):
        pass