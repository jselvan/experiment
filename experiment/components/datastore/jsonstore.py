import json 
from pathlib import Path
from experiment.components.datastore import DataStore


class JSONDataStore(DataStore):
    def __init__(self, session_directory, summary_function=None):
        super().__init__(summary_function=summary_function)
        self.session_directory = Path(session_directory)
    @property
    def json_path(self):
        return self.session_directory / "data.json"
    def get_summary(self):
        return self.summary
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