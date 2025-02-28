from collections.abc import Mapping
from typing import Any
class TaskManager:
    def select_profile(self):
        subjects = self.manager.config.get('subjects')
        if len(subjects) == 1 and subjects[0] is None:
            subject = None
        else:
            if self.manager.identifier is None:
                raise ValueError("If subject specific profiles are provided, an identifier must be available")
            subject = self.manager.identify()
        profile = self.manager.config.get('profiles').get(subject)
        return profile
    def select_trial(self) -> "Trial":
        profile = self.select_profile()
        # update block if necessary
        # determine the condition selection rule
        # if necessary look at previous behaviour
        # return a trial object
        trial = profile.get('trial')
        return trial
    def select_block(self):
        # determine block change rule
        # check if it meets change criterion
        # update block
        # return block object
        pass
    def wait_for_trial_init(self):
        pass
    def run_trial(self, trial: "Trial") -> Mapping[str, Any]:
        try:
            result = trial.execute(self.manager)
        except Exception as e:
            self.manager.logger.log_event(
                "TaskError",
                {"message": str(e), "trial": str(trial)}
            )
            raise
        return result
    def main(self):
        # wait for subject to initiate a trial
        self.wait_for_trial_init()
        # once a subject has initiated a trial
        # we will generate a trial for the subject
        trial = self.select_trial()
        # run this trial until it ends
        result = self.run_trial(trial)
        # we get some data for determining 
        # what we do next
        # for now we only implement going to an ITI 
        #TODO: implement bypassing ITI/subject identification?
        self.run_iti(result.get('ITI'))

