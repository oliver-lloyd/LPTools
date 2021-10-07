import argparse
import pandas as pd
from numpy import abs

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('query_scores', type=str)
    parser.add_argument('target_triples', type=str)
    parser.add_argument('raw_data_mr', type=str)
    parser.add_argument('raw_data_gc', type=str)
    parser.add_argument('--addins', type=bool, default=False)
    args = parser.parse_args()

    # Load in query scores and select relevant portion
    scores = pd.read_csv(args.query_scores)
    scores = scores.loc[scores.working_edge == args.addins]
    scores = scores.sort_values('score', ascending=args.addins).reset_index(drop=True)

    # Load in triples of interest and mark them in the scores table
    scores['target'] = False
    target_triples = pd.read_csv(args.target_triples, sep='\t', header=None)
    target_triples.columns = ['s', 'p', 'o']
    for i, row in target_triples.iterrows():
        scores_index = scores.query(f's == \'{row["s"]}\' & p == \'{row["p"]}\' & o == \'{row["o"]}\'').index[0]
        scores['target'].loc[scores_index] = True
        
    assert sum(scores.target) == len(target_triples)

    # Load in raw attribute info
    mr_raw_data = pd.read_csv(args.raw_data_mr, header=None)
    mr_raw_data.rename(columns={0: 's', 1: 'o', 8:'mr_pval'}, inplace=True)
    mr_raw_data['p'] = 'MREVE_1e-05'

    gc_raw_data = pd.read_csv(args.raw_data_gc, header=None)
    gc_raw_data.rename(columns={11: 's', 12: 'o', 5:'gen_cor'}, inplace=True)
    gc_raw_data['p'] = 'GenCor_0.5'

    # Merge raw data onto scores table
    merged_scores = scores.merge(mr_raw_data, how='left', on=['s', 'p', 'o'])
    merged_scores = merged_scores.merge(gc_raw_data, how='left', on=['s', 'p', 'o'])
    merged_scores.reset_index(drop=True, inplace=True)
    del mr_raw_data, gc_raw_data

    # Set up storage variables
    adj_rank = 1
    counter = 0
    attribute_loss = {p:0 for p in target_triples.p.unique()}
    target_triples['adjusted_rank'] = None
    target_triples['attribute_loss'] = None
    num_targets = len(target_triples)

    # Iterate through scores table, calculate rank losses, stitch them to knockout table
    for i, row in merged_scores.iterrows():

        # If row represents addin/knockout, store current loss values and continue
        if row.target:
            query = f's == \'{row["s"]}\' & p == \'{row["p"]}\' & o == \'{row["o"]}\''
            target_index = target_triples.query(query).index[0]
            target_triples['adjusted_rank'][target_index] = adj_rank
            target_triples['attribute_loss'][target_index] = attribute_loss[row['p']]
            counter += 1
        else:  # Otherwise increment corresponding loss value depending on type of edge
            adj_rank += 1
            if row['p'].startswith('MREVE'):
                if pd.isna(row.mr_pval):
                    pval_increment = 0.99995
                else:
                    pval_increment = row.mr_pval - 5e-5
                attribute_loss[row['p']] += pval_increment
            else:  
                if pd.isna(row.gen_cor):
                    gc_increment = 0.5
                else:
                    gc_increment = 0.5 - abs(row.gen_cor)
                attribute_loss[row['p']] += gc_increment

        # Break if found all target triples, otherwise print update
        if counter == num_targets:
            print('Found all target triples. Saving...')
            break
        elif not i % 1000:
            print(f'Processed {i} query scores, found {counter}/{num_targets} target triples so far.')
            
    target_triples.to_csv('results_attribute_rank_loss.csv', index=False)