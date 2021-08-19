import pandas as pd
import os
import argparse
import yaml
from numpy import nan
from nested_lookup import nested_lookup
import warnings

if __name__ == "__main__":
    
    warnings.filterwarnings("ignore")

    # Get user args
    parser = argparse.ArgumentParser(description='Dump results and stitch them to parameter configuration data.')
    parser.add_argument('experiments', metavar='F', type=str, nargs='+',
                        help='LibKGE experiment folder(s) of interest.')
    parser.add_argument('--result_path', metavar='r', type=str, nargs=1,
                        help='Path to results dir.', default='/bp1store/mrcieu1/users/fu19841/results/')
    parser.add_argument('--complete_unfinished', metavar='c', type=bool, nargs=1,
                        help='Whether to resume experiment if unfinished trials are detected.', default=False)
    args = parser.parse_args()
    
    # Process args
    if 'all' in args.experiments:
        # Process all experiment folders
        files_to_process = [loc for loc in os.listdir(args.result_path) if os.path.isdir(args.result_path + loc) and loc.startswith('202')]
    else:
        files_to_process = args.experiments
    
    if type(args.result_path) == list:
        args.result_path = args.result_path[0]


    # Iterate though list of experiments
    for experiment in files_to_process:
        if experiment.endswith('.csv') or experiment == 'processed':
            continue
        
        print(f'Processing {experiment}')

        if not experiment.startswith(args.result_path):
            path_to_this_experiment = f'{args.result_path}/{experiment}/'
            path_to_this_result = f'{args.result_path}/{experiment}.csv'
        else:
            path_to_this_experiment = experiment + '/'
            path_to_this_result = f'{experiment}.csv'
        
        # Check experimental results have not already been processed
        if f'{experiment}.csv' not in os.listdir(f"{args.result_path}"):
            # Use LibKGE command to dump basic results to file
            os.system(f'kge dump trace {path_to_this_experiment} > {path_to_this_result}')
            print(f'Dumped results for {experiment}')
        else:
            print(f"{experiment} has already been processed, skipping to next.")
            continue

        # Load relevant search space, find params of interest
        with open(f'{path_to_this_experiment}/config.yaml') as file:
            parameters = yaml.load(file, yaml.FullLoader)['ax_search']['parameters']
        non_fixed_params = [parameter['name'] for parameter in parameters if parameter['type'] != 'fixed']

        # Load results, add columns for config params
        results = pd.read_csv(path_to_this_result)
        for param in non_fixed_params:
            results[param] = nan

        # Iterate though experiment trials
        non_best_trials = []
        for loc in os.listdir(path_to_this_experiment):
            try:
                trial_number = int(loc)
            except ValueError:
                continue

            # Check if trial is valid and finished
            valid_trial_check = os.path.isdir(path_to_this_experiment + loc) and trial_number in results.child_folder
            if not valid_trial_check and args.complete_unfinished:
                print(f'Trial {loc} not found in trace. Resuming experiment...')
                os.system(f'kge resume {path_to_this_experiment}')
            elif not valid_trial_check:
                raise FileNotFoundError(f'Trial {loc} not found in the experiment trace. Experiment is likely unfinished, please finish before re-running this script')
            else:
                # Load config data
                row = results.loc[results.child_folder == trial_number]
                child_job_id = row['child_job_id'].iloc[0]
                with open(path_to_this_experiment + loc + f'/config/{child_job_id}.yaml') as file:
                    config = yaml.load(file, yaml.FullLoader)

                # Check performance, delete all checkpoint if not best trial
                if row.metric.iloc[0] != max(results.metric):
                    os.system(f"rm {path_to_this_experiment}/{loc}/*.pt")
                else:
                    os.system(f"rm {path_to_this_experiment}/{loc}/checkpoint_0*.pt")
                

                # Get values for each parameter of interest and store in results
                for param in non_fixed_params:
                    keys = param.split('.')
                    value = config
                    for key in keys:
                        try:
                            value = value[key]
                        except KeyError:
                            target_key = keys[-1]
                            value = nested_lookup(target_key, value)
                            if len(value) == 1:
                                value = value[0]
                            break
                    if param == 'train.optimizer':
                        value = nested_lookup('type', value)[0]
                    
                    # Check for type of returned value
                    try:
                        results[param][trial_number] = value
                    except ValueError:
                        print(
                            f"{param} could not be properly parsed. The resulting dictionary has been converted to a string.")
                        results[param][trial_number] = str(value)

        # Write results to file
        results.to_csv(path_to_this_result, index=False)
