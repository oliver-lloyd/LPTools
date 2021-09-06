# bash4libkge
This directory contains command-line tools, written in Bash, that facilitate analysis with LibKGE.

---
## switch_start/resume.sh
When running LibKGE experiments on a PBS server, these tools will edit the specified job scripts to either switch the command `kge start <config file>` to `kge resume <existing experiment>`, or vice versa. 

---
TODO:
- switch_start_resume.sh
    - exp_dir should be passed as an argument
- switch_resume_start.sh
    - conf_dir should be passed as an argument