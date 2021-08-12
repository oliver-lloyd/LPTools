import pandas as pd
import argparse
import warnings

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    
    # Get user args
    parser = argparse.ArgumentParser(
        description='Scores addin predictions outputted from link_scorer.py')
    parser.add_argument('Edge_scores', metavar='P', type=str,
                        help='Output file from py4libkge/link_scorer.py --addins')
    parser.add_argument('Output_directory', metavar='o', type=str)
    args = parser.parse_args()

    # Read in model scores and sort by reverse score
    scores = pd.read_csv(args.Edge_scores)
    scores = scores.sort_values('score', ascending=True).reset_index(drop=True)

    # Create results frame 
    addin_results = scores[['s', 'p', 'o', 'score']].loc[scores.addin == True]
    addin_results['reverse_rank'] = addin_results.index

    # Adjust so as not to penalise for ranking below other addin edges
    addin_results['adjusted_reverse_rank'] = None
    addin_results.reset_index(inplace=True, drop=True)
    for i, row in addin_results.iterrows():
        adjusted_reverse_rank = row.reverse_rank - i  
        addin_results.adjusted_reverse_rank[i] = adjusted_reverse_rank
    
    # Caluculate MRR
    addin_results['mean_reciprocal_adjusted_reverse_rank'] = 1/addin_results.adjusted_reverse_rank

    # Save
    addin_results.to_csv(args.Output_directory + '/addin_results.csv', index=False)