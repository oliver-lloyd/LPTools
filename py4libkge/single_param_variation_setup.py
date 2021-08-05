import argparse
import pandas as pd
import os
import yaml
from subprocess import check_output
from nested_lookup import nested_lookup


def get_best_config(result_file):
    results_path = '/bp1store/mrcieu1/users/fu19841/results/LPComparison/'
    path_to_result_file = results_path + result_file
    results = pd.read_csv(path_to_result_file)
    best_result = results.loc[results.metric == max(results.metric)]
    best_job_id = best_result.child_job_id.iloc[0]

    path_to_experiment_folder = path_to_result_file.replace('.csv', '/')
    path_to_best_config = str(check_output(f'find {path_to_experiment_folder} -name "{best_job_id}.yaml"', shell=True))[2:-3]
    with open(path_to_best_config) as f:
        config_yaml = yaml.load(f, yaml.FullLoader)
        
    return config_yaml


def setup_single_param_yamls(og_config, num_trials=100):

    parameter_spaces = og_config['ax_search']['parameters']
    varying_params = [param for param in parameter_spaces if param['type'] != 'fixed']
    for single_param in varying_params:
        new_config = og_config
        if single_param['type'] == 'choice':
            num_trials = len(single_param['values']) * 10
        else:
            num_trials = 100
        new_config['ax_search']['num_trials'] = num_trials
        new_config['ax_search']['num_sobol_trials'] = num_trials
        for param in varying_params:
            new_fixed_param = {
                'name':param['name'],
                'type':'fixed',
                'value': None
            }
            keys = param['name'].split('.')
            value = og_config
            for key in keys:
                try:
                    value = value[key]
                except KeyError:
                    target_key = keys[-1]
                    value = nested_lookup(target_key, value)
                    if len(value) == 1:
                        value = value[0]
                    break
            if param['name'] == 'train.optimizer':
                value = nested_lookup('type', value)[0]
            if type(value) == dict:
                raise ValueError("Couldn't parse fixed parameter value")
            new_fixed_param['value'] = value
            params_to_remove = [param for param in new_config['ax_search']['parameters'] if param['name'] in [new_fixed_param['name'], single_param['name']]]
            for param_drop in params_to_remove:
                new_config['ax_search']['parameters'].remove(param_drop)
            new_config['ax_search']['parameters'].append(new_fixed_param)
        new_config['ax_search']['parameters'].append(single_param)
        new_config['job']['type'] = 'search'
        new_yaml_name = f"{new_config['model']}_{new_config['dataset']['name']}_{single_param['name'].replace('.','_')}.yaml"
        with open(f'/bp1store/mrcieu1/users/fu19841/kge/local/experiments/{new_yaml_name}', 'w') as f:
            yaml.dump(new_config, f)        


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get best config file from an experiment.')
    parser.add_argument('files', metavar='F', type=str, nargs='+',
                        help='Results .csv files to process.')

    args = parser.parse_args()
    for csv in args.files:
        best_config = get_best_config(csv)
        setup_single_param_yamls(best_config)
