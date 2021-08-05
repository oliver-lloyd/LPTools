import yaml
import argparse

# TODO: add arg parsing

if __name__ == "__main__":
    path_to_experiments = '/bp1store/mrcieu1/users/fu19841kge/local/experiments/'
    file_name = 'template_gridsearch.yaml'
    with open(path_to_experiments + file_name) as f:
        file_template = f.read()

    models = [
        "conve", "cp", "distmult", "reciprocal_relations_model",
        "relational_tucker3", "rescal", "rotate", "simple", "transe",
        "transformer", "transh" 
    ]
    datasets = ['umls', 'fb15k-237', 'wnrr']
    for model_name in models:
        for dataset_name in datasets:
            new_file_name = model_name + '_' + dataset_name + '_gridsearch.yaml'
            new_yaml = file_template.replace('model_name', model_name).replace('dataset_name', dataset_name)
            with open(path_to_experiments + new_file_name, 'x') as new_f:
                new_f.write(new_yaml)
