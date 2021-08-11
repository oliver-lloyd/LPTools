import pandas as pd
import argparse
import warnings

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    
    # Get user args
    parser = argparse.ArgumentParser(
        description='Scores addin predictions outputted from link_scorer.py')
    parser.add_argument('Predictions', metavar='P', type=str,
                        help='Output file from py4libkge/link_scorer.py')
    parser.add_argument('Output_directory', metavar='o', type=str)
    args = parser.parse_args()

    #TODO: finish