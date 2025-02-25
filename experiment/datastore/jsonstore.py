import json 
from experiment.datastore.base import DataStore

class JSONDataStore(DataStore):
    def __init__(self, session_directory):
        self.session_directory = session_directory
        self.json_path = session_directory / "data.json"
        self.keys = []
        self.records = {}
        self.trialid = 0
    @property
    def current_trial_record(self):
        if self.trialid not in self.records:
            self.records[self.trialid] = {"trialid": self.trialid}
        return self.records[self.trialid]
    def record(self, **kwargs):
        for k in kwargs:
            if k not in self.keys:
                self.keys.append(k)
        self.current_trial_record.update(kwargs)
    def flush(self):
        if not self.json_path.exists():
            with open(self.json_path, 'w') as f:
                f.write("[")
        else:
            with open(self.json_path, 'a') as f:
                f.write(",\n")
        with open(self.json_path, 'a') as f:
            json.dump(self.current_trial_record, f)
    def close(self):
        with open(self.json_path, 'a') as f:
            f.write("]")
    def link_attachment(self, name, ftype) -> str:
        pass
