import json 
from pathlib import Path
from experiment.datastore.base import DataStore

def default_summary_function(self):
    n_trials = len(self.records)
    self.summary = {'n_trials': n_trials}

class JSONDataStore(DataStore):
    def __init__(self, session_directory, summary_function=None):
        self.session_directory = Path(session_directory)
        self.key_is_scalar = {}
        self.records = {}
        self.trialid = 0
        if summary_function is None:
            self.summary_function = default_summary_function
        else:
            self.summary_function = summary_function
        self.summary = {}
    @property
    def json_path(self):
        return self.session_directory / "data.json"
    @property
    def current_trial_record(self):
        if self.trialid not in self.records:
            self.records[self.trialid] = {"trialid": self.trialid}
        return self.records[self.trialid]
    def get_summary(self):
        return self.summary
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
    def flush(self):
        self.key_is_scalar = {}
        if not self.json_path.exists():
            with open(self.json_path, 'w') as f:
                f.write("[")
        else:
            with open(self.json_path, 'a') as f:
                f.write(",\n")
        with open(self.json_path, 'a') as f:
            json.dump(self.current_trial_record, f)
        self.summary_function(self)
    def close(self):
        with open(self.json_path, 'a') as f:
            f.write("]")
    def link_attachment(self, name, ftype) -> str:
        pass
