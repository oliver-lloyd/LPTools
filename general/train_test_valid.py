import pandas as pd
import argparse
from sklearn.model_selection import train_test_split


def split_and_write(edge_list, output_dir):

    train_valid, test = train_test_split(edge_list, test_size=0.035)
    train, valid = train_test_split(train_valid, test_size=0.04)

    train.to_csv(output_dir + '/train.txt', header=None, index=None, sep='\t')
    valid.to_csv(output_dir + '/valid.txt', header=None, index=None, sep='\t')
    test.to_csv(output_dir + '/test.txt', header=None, index=None, sep='\t')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('edgelist_path', type=str)
    parser.add_argument('output_directory', type=str)
    args = parser.parse_args()

    edges = pd.read_csv(args.edgelist_path, header=None, sep='\t')

    split_and_write(edges, args.output_directory)
