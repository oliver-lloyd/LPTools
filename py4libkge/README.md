# py4libkge
This directory contains command-line tools, written in Python, that facilitate analysis with LibKGE.

---
## addin_assessor.py
Processes `addin_all_edge_scores.csv` (which is created by `link_scorer.py` when the `--addins` flag is used), and returns a results file for a given addin experiment. Takes the aforementioned file as the first argument, followed by an output directory.

---
## job_creator.py
Creates a PBS job file for each of the LibKGE config files passed as an argument.

---
## knockout_assessor.py
Processes `knockout_preds.csv` (which is created by `link_scorer.py`), and returns a results file for a given knockout experiment. First argument should be the aforementioned file, followed by the relevant edgelist (AFTER edges have been knocked), and finally an output directory.

---
## link_scorer.py
Uses a trained model from LibKGE to make predictions (scores) for a given set of knockouts/addins. This will be in the form of a PyTorch file (`.pt`) and should be passed as the first argument. The next argument is the triples being tested- for knockout experiments this is simply the list of knocked out edges, but for addin experiments this MUST be the full edgelist including added-in edges. This is because addin scores are meaningless without the scores of the other triples to give them context. An output directory should be passed next. If the experiment is addin, the `--addins` flag should be used at the end, specifying the file containing the added-in edges.

---
## process_job_output.py
Note: do NOT use this script in its current state- manual review of output files is the best course of action.

Processes the output files returned from PBS regarding LibKGE jobs and takes action according to the state of the experiment upon job completion.

---
## process_results.py
An extension of LibKGE's built-in `kge dump trace` command. This script gathers up additional information regarding gridsearches (such as parameter values at each trial) and stitches it to the default trace output. One or more LibKGE experiments should be passed as an argument.

---
## reduce_batch_size.py
Removes the highest value of the `train.batch_size` parameter in the ax-search sections of the LibKGE config files passed as an argument. This is useful when running into CUDA memory errors on experiments.

---
## shrink_experiment_size.py
PyTorch checkpoint files can be up to 1/2Gb in size each, and LibKGE gridsearches store a lot of them which can quickly bloat experiment folders. This script deletes redundant checkpoints, saving only the best performing ones (determined by output from `kge dump trace`) from the experiments passed as an argument.

Note that `process_results.py` also deletes all non-best checkpoints, so if an experiment is finished then `shrink_experiment_size.py` is redundant and should not be run.

---
## single_param_variation_setup.py
Redundant file, used in pilot study to create jobs where only one parameter at a time was 
varied.

---
TODO:
- reduce_batch_size.py
    - Need to implement method for locating batch size parameter, it wont always be on index 1 
- Paths in all scripts should be modifiable via arguments.