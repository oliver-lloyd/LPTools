# Steps for running LibKGE gridsearches on bluepebble.



## 1) Set up config files
Either manually or using `py4libkge/yaml_setup.py`, set up the `.yaml` files to specify the desired model, dataset, and range of parameters to be tested.

Update 19 April:
Yamls should now be created using `create_config_files.py` inside a particular subdirectory of `.../scripts/config_files`. From there, all the YAML files can be copied to the experiment directory with `cp */*/*.yaml {experiment_path}`.

## 2) Create job files
Running `py4libkge/job_creator.py` will automatically create job files in `~/jobs` from the `.yaml` files in the experiment directory.

## 3) Submit job files
Either manually or with `~/submit_jobs.py`, which takes the path to the job file(s) as an argument.

## 4) Process job output files
Run `py4libkge/process_job_output.py` in the directory containing the output files from the submitted jobs. This will move job files to storage if the job will not be run again. Jobs that ran out of memory will automatically have their configurations edited to have double the previous memory, and can then be resubmitted.


## 5) Repeat steps 3-4 
Do this until all experiments have sucessfully run.

## 6) Export results
Run `py4libkge/process_results.py` to run LibKGE's `dump trace` command on the experiment folders you passed as an argument. This script will also dive into the specific configurations for each trial of the gridsearch, stitching this information to the relevant rows of the `.csv` that LibKGE dumps by default.