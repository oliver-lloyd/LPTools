import argparse
import os

def delete_non_best_checkpoints(experiment_folder, max_trial=None):
    """
    Storage of redundant PyTorch checkpoints may inflate LibKGE experiment folder sizes beyond 
    what is reasonable. This function deletes them. 
    """

    for loc in os.listdir(experiment_folder):
        try:
            # Check loc is a trial
            int(loc)
        except ValueError:
            # Skip if not
            continue
        if (max_trial or max_trial == 0) and int(loc) > max_trial:
            # Also skip if max trial exceeded
            continue

        # Delete all checkpoints without 'best' in name
        for sub_loc in os.listdir(f"{experiment_folder}/{loc}"):
            if sub_loc.endswith('.pt') and sub_loc.startswith('checkpoint_') and 'best' not in sub_loc:  
                os.system(f"rm {experiment_folder}/{loc}/{sub_loc}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Shrink LibKGE experiment folders.')
    parser.add_argument('experiments', metavar='E', type=str, nargs='+',
                        help='Experiment folder(s).')
    parser.add_argument('--max_trial', metavar='M', type=int,
                    help='Highest trial number to shrink')
    args = parser.parse_args()

    for experiment in args.experiments:
        if os.path.isdir(experiment):
            delete_non_best_checkpoints(experiment, args.max_trial)
    
        