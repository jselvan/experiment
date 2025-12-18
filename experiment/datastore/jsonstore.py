import json 
from pathlib import Path
from experiment.datastore.base import DataStore

class JSONDataStore(DataStore):
    def __init__(self, session_directory):
        self.session_directory = Path(session_directory)
        self.key_is_scalar = {}
        self.records = {}
        self.trialid = 0
    @property
    def json_path(self):
        return self.session_directory / "data.jsonl"
    @property
    def current_trial_record(self):
        if self.trialid not in self.records:
            self.records[self.trialid] = {"trialid": self.trialid}
        return self.records[self.trialid]
    @property
    def previous_trial_record(self):
        if self.trialid - 1 not in self.records:
            return None
        return self.records[self.trialid - 1]
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
        with open(self.json_path, 'a') as f:
            json.dump(self.current_trial_record, f)
            f.write("\n")
    def close(self):
        pass
    def link_attachment(self, name, ftype) -> str:
        ... # Implementation for linking attachments
