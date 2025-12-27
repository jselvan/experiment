import random
from collections import ChainMap
from typing import Dict, Any, TYPE_CHECKING
from experiment.util.python_import_helper import load_object_from_module

if TYPE_CHECKING:
    from experiment.trial import Trial, TrialResult

class BlockManager:
    DEFAULT_METHOD = 'incremental'
    def __init__(self, 
        config: Dict[str, Any], 
        trials: "Dict[str, type[Trial]]"
    ):
        blocks = config['blocks']
        self.conditions = config['conditions']
        self.blocks = blocks
        self.defaults = config
        self.block_names = list(blocks.keys())
        self.block_list = [blocks[name] for name in self.block_names]
        self.current_block_number = 0
        self.current_block_idx = 0
        self.trial_in_block = 0
        self.n_trials_completed = 0
        self.trials = trials

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "BlockManager":
        trial_spec  = config.get('trial_types', {})
        trials = {}
        for name, trial_cls_params in trial_spec.items():
            trials[name] = load_object_from_module(
                trial_cls_params['module'], 
                trial_cls_params['class']
            )
        return cls(config, trials)

    @property
    def current_block(self):
        return self.block_list[self.current_block_idx]

    @property
    def current_block_name(self):
        return self.block_names[self.current_block_idx]
    
    def increment_trial(self):
        self.trial_in_block += 1
        if self.trial_in_block >= self.current_block['length']:
            self.next_block()
    
    def parse_results(self, result: "TrialResult"):
        self.n_trials_completed += 1
        outcome = result.outcome
        retry = self.current_block.get('retry', {}).get(outcome, False)
        if not retry:
            self.increment_trial()

    def next_block(self):
        self.current_block_idx = (self.current_block_idx + 1) % len(self.blocks)
        self.current_block_number += 1
        self.trial_in_block = 0
    
    def get_next_condition(self):
        method = self.current_block.get('method', self.DEFAULT_METHOD)
        if method == 'incremental':
            condition_idx = self.trial_in_block % len(self.current_block['conditions'])
        elif method == 'random':
            condition_idx = random.randint(0, len(self.current_block['conditions'])-1)
        else:
            raise ValueError(f"Unknown method {method}")
        condition_name = self.current_block['conditions'][condition_idx]
        condition = self.conditions[condition_name]
        condition = dict(ChainMap(condition, self.current_block, self.defaults))
        return condition_name, condition

    def get_next_trial(self) -> "Trial":
        condition_name, condition = self.get_next_condition()
        trial_type = condition.get('trial_type', 'default')
        assert isinstance(trial_type, str)
        if trial_type not in self.trials:
            raise ValueError(f"Unknown trial type {trial_type}")
        trial = self.trials[trial_type].from_config(condition)
        return trial, condition_name, condition