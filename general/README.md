# General tools
These Python-based tools are useful for any link prediction analyses, whether or not you are working with LibKGE.

---
## random_knockout.py
Taking an edgelist (tab separated, no header) as a required argument, this script will select a number of random edges (default is 10, modify with `--num_knockouts` flag) and remove them from the list. The resultant edgelist will be saved under the original name plus the suffix `_knocked_out_10.tsv`. A list of the knocked out edges will be saved as `10_knockouts.tsv`.

---
## random_addin.py
Behaving in much the same way as `random_knockout.py`, this script will generate random new edges (10 default, modify with `--num_addins`) and append them to the specified edgelist, saving with the suffix `_added_in_10.tsv`. The added in edges will be saved as `10_addins.tsv`. New edges will only include nodes and relations that already exist in the edgelist, so there will be no issue of unseen entities.

---
## train_test_valid.py
Using scikit-learn's `train_test_split` function, this tool takes an input edgelist and splits it into three sets: training, testing, and validation. These split edgelists are then saved in the directory provided as the second argument. Though tab-separated, these edgelists are saved with `.txt` suffixes for compatability with LibKGE.

---

TODO:
- Add an argument for test/valid proportions to train_test_valid.py