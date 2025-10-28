from pathlib import Path
import time

def load_trial(module_path, class_name):
    import importlib.util
    spec = importlib.util.spec_from_file_location("trial_module", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {module_path}")
    trial_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trial_module)
    trial_class = getattr(trial_module, class_name)
    return trial_class

def get_block(blocks, block_idx):
    current_block_info = blocks[block_idx].copy()
    current_block_info['trial_in_block'] = 0
    return current_block_info

def run_with_task_config(mgr, task_config, task_directory):
    default_trial = {'module_path': task_directory / 'trial.py', 'class_name': 'Trial'}

    blocks = task_config.get('blocks', None)
    conditions = task_config.get('conditions', None)
    if conditions is None:
        raise ValueError("No conditions specified in task configuration.")

    if blocks is None:
        # no blocks specified, we assume a single block
        # with some sane default parameters
        block = {
            'length': 100,
            'retry': {}, # we do not retry any trials by default
            'method': 'incremental',
            'conditions': list(conditions.keys()) # use all conditions
        }
        block.update(task_config.get('defaults', {}))
        blocks = [block]

    default_timings = task_config.get('timings', {'iti': 1})

    
    trialid = 0
    block_number = 0
    block_idx = 0
    current_block_info = get_block(blocks, block_idx)
    condition = current_block_info['conditions'][0]

    continue_experiment = True
    mgr.initialize()
    mgr.start_session()
    while continue_experiment:
        # set up trial
        trial_info = conditions.get(condition).copy()
        trial_info.update(current_block_info.get('defaults', {})) # block defaults override condition defaults

        mgr.record(
            trialid=trialid, 
            block=block_idx, 
            block_number=block_number, 
            condition=condition, 
            trial_in_block=current_block_info['trial_in_block']
        )
        if default_timings is not None:
            trial_info.setdefault('timings', default_timings)

        trial_class_info = trial_info.get('trial_class', default_trial)
        trial_class = load_trial(
            module_path=trial_class_info['module_path'],
            class_name=trial_class_info['class_name']
        )
        trial = trial_class(**trial_info)
        continue_experiment = mgr.run_trial(trial)
        time.sleep(trial.timings['iti'])

        # update for next trial
        trialid += 1
        block_number += 1
        if block_number >= current_block_info['length']:
            block_idx += 1
            if block_idx >= len(blocks):
                break
            current_block_info = blocks[block_idx]
            block_number = 0
        condition = current_block_info['conditions'][block_number % len(current_block_info['conditions'])]


def run(task_directory, system_config=None):
    task_directory = Path(task_directory).expanduser()
    # first we need to set up the manager
    # the manager will first look for a system config file in the task directory
    task_system_config = task_directory / "system_config.toml"
    default_system_config = Path("~/experiment/config/system_config.toml").expanduser()
    minimal_system_config = Path(__file__).parent.parent / "minimal_system_config.toml"

    if system_config is not None: 
        # If the user has provided a system config path, use that, otherwise look for one
        system_config = Path(system_config).expanduser()
    elif task_system_config.exists():
        system_config = task_system_config
    elif default_system_config.exists():
        system_config = default_system_config
    elif minimal_system_config.exists():
        system_config = minimal_system_config
    else:
        raise FileNotFoundError("No system configuration file found.")
    
    import tomllib
    with open(system_config, 'rb') as f:
        config = tomllib.load(f)
    from experiment.manager import Manager
    manager = Manager.from_config(config)

    # now we can load the task info
    # by default we want to look for a task_config.toml file in the task directory
    task_config_file = task_directory / "task_config.toml"
    if task_config_file.exists():
        with open(task_config_file, 'rb') as f:
            task_config = tomllib.load(f)
        return run_with_task_config(mgr=manager, task_config=task_config, task_directory=task_directory)

    # we did not find a task config file, we now look for a trial_selector.py file
    trial_selector_file = task_directory / "trial_selector.py"
    trial_selector_function_name = "select_trial"
    if trial_selector_file.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("trial_selector_module", trial_selector_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {trial_selector_file}")
        trial_selector_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(trial_selector_module)
        select_trial_function = getattr(trial_selector_module, trial_selector_function_name)
        raise NotImplementedError("Trial selector based tasks are not yet implemented.")
    
    raise FileNotFoundError("No task configuration file or trial selector found in task directory.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run an experiment task.")
    parser.add_argument('task_directory', type=str, help="Path to the task directory.")
    parser.add_argument('--system-config', type=str, default=None, help="Path to the system configuration file.")
    args = parser.parse_args()
    run(task_directory=args.task_directory, system_config=args.system_config)