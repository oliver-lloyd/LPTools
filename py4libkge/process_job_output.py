from os import system, path, listdir
import glob
import yaml
import argparse

def delete_experiment(name, path_string):
    from os import path, listdir
    for loc in listdir(path_string):
        if name in loc and path.isdir(path_string + loc):
            system(f'rm -r {path_string}{loc}')

            
if __name__ == "__main__":
    # Get user args
    parser = argparse.ArgumentParser(description='Automatically process job output files.')
    parser.add_argument('files', metavar='F', type=str, nargs='+',
                        help='*.sh.* files to process..')
    parser.add_argument('--mem_increase', metavar='M', type=float, nargs=1,
                        help='Factor to scale job memory by')

    # Set paths
    home_path = '/home/fu19841/'
    py4libkge_path = f'{home_path}/LPComparison/scripts/py4libkge/'
    experiment_path = '/bp1store/mrcieu1/users/fu19841/kge/local/experiments/'

    args = parser.parse_args()
    if args.mem_increase:
        memory_scale = args.mem_increase
        if type(memory_scale) == list:
            memory_scale = memory_scale[0]
    else:
        memory_scale = 2
    files_to_process = [home_path + file for file in args.files]

    for output_file_name_with_path in files_to_process:
        output_file_name = output_file_name_with_path.split('/')[-1]
        with open(output_file_name) as f:
            job_output = f.read()
        job_file_name = output_file_name.split('.')[0] + '.sh'
        experiment_name = job_file_name.split('.')[0]
        yaml_name = job_file_name.split('.')[0] + '.yaml'
        

        # First check output for exceeding CUDA memory, shrinking batch size if it has
        if job_output.count('CUDA out of memory') >= 1:  
            print('OLLIE: batch size is a changing param in gridsearch1, figure out what to do about this CUDA memory error.')
            continue
            
            with open(experiment_path + yaml_name) as f:
                yaml_contents = yaml.load(f, Loader=yaml.FullLoader)

            current_batch_size = yaml_contents['train']['batch_size']
            new_batch_size = int(current_batch_size / 4)
            yaml_contents['train']['batch_size'] = new_batch_size
            print(f'Batch size decreased from {current_batch_size} to {new_batch_size} in {yaml_name}. Ready to resubmit job.')

            with open(experiment_path + yaml_name, 'w+') as new_f:
                yaml.dump(yaml_contents, new_f)

            # Delete experiment folder
            #delete_experiment(experiment_name, experiment_path)

        # Next check for PBS running out of memory, doubling allocated memory if it has
        if job_output.count('PBS: job killed: mem') >= 1: 
            with open(f'{home_path}jobs/{job_file_name}') as f:
                file_contents = f.read()
            current_mem = int(file_contents.split('mem=')[1].split('gb')[0])
            current_mem_string = f'mem={current_mem}gb'
            new_mem = int(current_mem * memory_scale)
            new_mem_string = f'mem={new_mem}gb'
            new_file_contents = file_contents.replace(current_mem_string, new_mem_string)
            exp_folder = [dir for dir in listdir(experiment_path) if experiment_name in dir and path.isdir(experiment_path + dir)][0]
            new_file_contents = new_file_contents.replace('kge start', 'kge resume')
            new_file_contents = new_file_contents.replace(yaml_name, exp_folder)
            with open(f'{home_path}jobs/{job_file_name}', 'w+') as f:
                f.write(new_file_contents)
            system(f"qsub -q mrcieu {home_path}jobs/{job_file_name}")
            print(f'Resubmitted {job_file_name}, resumed {experiment_name} with {new_mem_string}')
            #system(f'rm {output_file_name_with_path}')

        # Check for other Python errors, moving files to 'errored' directory for manual inspection
        if job_output.count('Traceback (most recent call last):') >= 1:  
            print(f'Found Python error: ignoring {output_file_name}')
            continue  # TODO: Refine this functionality before use
      
        #if path.exists(output_file_name_with_path):
            #system('rm ' + output_file_name_with_path)
