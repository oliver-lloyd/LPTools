import pandas as pd
import argparse
import warnings

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    
    # Get user args
    parser = argparse.ArgumentParser(
        description='Replaces entity IDs with corresponding names for test\
            entity rankings')
    parser.add_argument('Predictions', metavar='P', type=str,
                        help='Output file from py4libkge/link_scorer.py')
    parser.add_argument('Edgelist_without_knockouts', metavar='E', type=str,
                        help='Combined edges from train, test and valid splits')
    parser.add_argument('Output_directory', metavar='o', type=str,
                        help='Optional file name for output')  #TODO: Implement this
    args = parser.parse_args()

    # Load in data
    knockout_preds = pd.read_csv(args.Predictions)
    edgelist = pd.read_csv(args.Edgelist_without_knockouts, header=None, sep='\t')
    # Construct output dataframe
    knockout_result_assessment = knockout_preds[['s', 'p', 'o', 'query_type']]
    columns_to_add = [
        'rank', 'score_given', 
        'rank1_entity', 'rank1_score',
        'rank2_entity', 'rank2_score',
        'rank3_entity', 'rank3_score',
        'rank4_entity', 'rank4_score',
        'rank5_entity', 'rank5_score'
    ]
    for col in columns_to_add:
        knockout_result_assessment[col] = None  

    # Get set of existant edges
    existant_edges = [list(x) for x in edgelist.to_numpy()]


    # Iterate through knockouts, assessing model performance for each
    for i, row in knockout_preds.iterrows():
        knocked_edge = [row['s'], row['p'], row['o']]
        correct_entity = row['o']

        # Check for knockout leakage
        if knocked_edge in existant_edges:
            knockout_result_assessment.loc[i] = knocked_edge + ['sp_', 'NA: edge in training set'] + [None for _ in range(len(columns_to_add)-1)]

        else:
            # Order scores to check rank of correct entity
            scores = row[row.index[4:]].sort_values(ascending=False)

            top5_entities_and_scores = []
            rank = 1
            correct_entity_found = False
            correct_entity_score = None
            correct_entity_rank = None
            for entity_score_tup in zip(scores.index, scores.values):

                # Unpack values
                entity = entity_score_tup[0]
                score = entity_score_tup[1]

                # Update checking bool
                if entity == correct_entity:

                    correct_entity_found = True
                    correct_entity_score = score
                    correct_entity_rank = rank

                # Check if entity represents an existant edge, skip if yes
                edge_to_check = [row['s'], row['p'], entity]
                if edge_to_check in existant_edges:
                    continue
                else:
                    rank += 1

                if len(top5_entities_and_scores) < 10:
                    # Store top 5 scoring non-existant completing entities
                    top5_entities_and_scores.append(entity)
                    top5_entities_and_scores.append(score)

                if correct_entity_found and len(top5_entities_and_scores) == 10:
                    # Save result if have top 5 entities and have found correct_entity
                    result = knocked_edge + ['sp_', correct_entity_rank, correct_entity_score] + top5_entities_and_scores
                    knockout_result_assessment.loc[i] = result

            # Account for case where < 5 entities represented non-existant edges
            if len(top5_entities_and_scores) < 10:
                while len(top5_entities_and_scores) < 10:
                    top5_entities_and_scores.append(None)
                knockout_result_assessment.loc[i] = knocked_edge + ['sp_', correct_entity_rank, correct_entity_score] + top5_entities_and_scores

    knockout_result_assessment.to_csv(f'{args.Output_directory}/knockout_results.csv', index=False)