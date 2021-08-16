import yaml
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('Configs', metavar='F', type=str, nargs='+',
                    help='Config files to process.')
args = parser.parse_args()

for config_name in args.Configs:
    with open(config_name) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    config['ax_search']['parameters'][1]['values'] = config['ax_search']['parameters'][1]['values'][:-1]

    with open(config_name, 'w') as f:
        yaml.dump(config, f)