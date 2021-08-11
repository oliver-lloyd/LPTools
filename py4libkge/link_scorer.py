import argparse
import numpy as np
import pandas as pd
import torch

from kge.model import KgeModel
from kge.util.io import load_checkpoint


def prepare_sp_(edges, model):

    entity_mapper = {name: i for i, name in enumerate(
        model.dataset.entity_strings())}
    target_entity_ids = [entity_mapper[name] for name in edges[0]]
    s = torch.Tensor(target_entity_ids).long()

    relation_mapper = {name: i for i, name in enumerate(
        model.dataset.relation_strings())}
    target_relation_ids = [relation_mapper[name] for name in edges[1]]
    p = torch.Tensor(target_relation_ids).long()

    return s, p


def prepare__po(edges, model):

    entity_mapper = {name: i for i, name in enumerate(
        model.dataset.entity_strings())}
    target_entity_ids = [entity_mapper[name] for name in edges[2]]
    o = torch.Tensor(target_entity_ids).long()

    relation_mapper = {name: i for i, name in enumerate(
        model.dataset.relation_strings())}
    target_relation_ids = [relation_mapper[name] for name in edges[1]]
    p = torch.Tensor(target_relation_ids).long()

    return p, o


def prepare_s_o(edges, model):

    entity_mapper = {name: i for i, name in enumerate(
        model.dataset.entity_strings())}

    target_entity_ids_s = [entity_mapper[name] for name in edges[0]]
    s = torch.Tensor(target_entity_ids_s).long()

    target_entity_ids_o = [entity_mapper[name] for name in edges[2]]
    o = torch.Tensor(target_entity_ids_o).long()

    return s, o


def create_results_file(scores, model, query_type):

    cols = ['s', 'p', 'o', 'query_type']
    if query_type == 's_o':
        cols += model.dataset.relation_strings()
    else:
        cols += model.dataset.entity_strings()
    results = pd.DataFrame(columns=cols)

    for i_row, entity_scores in zip(input_triples.iterrows(), scores):
        row = list(i_row[1])
        row.append(query_type)
        row += list(entity_scores)
        results.loc[len(results)] = row

    return results


if __name__ == '__main__':
    # Get user args
    parser = argparse.ArgumentParser(
        description='Replaces entity IDs with corresponding names for test\
            entity rankings')
    parser.add_argument('Checkpoint', metavar='C', type=str,
                        help='Model checkpoint to load')
    parser.add_argument('Triple_file', metavar='T', type=str,
                        help='.tsv containing triples to test')
    parser.add_argument('Output_loc', metavar='O', type=str,
                        help='File path for output dir')
    parser.add_argument('--query_type', metavar='q', default='sp_', type=str,
                        help='File path for output')
    parser.add_argument('--edge_list', metavar='e', type=str, 
                        help='Edgelist of target graph. Only required if Triple_file == "all"')
    parser.add_argument('--addins', metavar='a', type=str, default=None, 
                        help='Whether this is an addin experiment instead of knockout')
    args = parser.parse_args()

    # Load model
    checkpoint = load_checkpoint(args.Checkpoint)
    kge_model = KgeModel.create_from(checkpoint)
    ents = kge_model.dataset.entity_strings()
    rels = kge_model.dataset.relation_strings()
    
    # Prepare queries
    if args.Triple_file == 'all':
        queries = [[ent, rel, '?'] for ent in ents for rel in rels]
        input_triples = pd.DataFrame(queries)
        output_file_name = '/all_query_scores.csv'
    else:
        input_triples = pd.read_csv(args.Triple_file, header=None, sep='\t')
        if args.addins:
            output_file_name = '/addin_all_edge_scores.csv'
            addins = pd.read_csv(args.addins, header=None, sep='\t')
            addins_list = [list(edge) for edge in addins.to_numpy()]
        else:    
            output_file_name = '/knockout_preds.csv'

            # In high-proportion knockout datasets, unseen entities are a problem
            # So remove them and store elsewhere
            unseen_knockouts = pd.DataFrame()
            for i, row in input_triples.iterrows():
                ents_check = row[0] in ents and row[2] in ents
                rel_check = row[1] in rels
                if not (ents_check and rel_check):
                    input_triples.drop(i, inplace=True)
                    unseen_knockouts = unseen_knockouts.append(row)
            num_unseen = len(unseen_knockouts)
            if num_unseen > 0:
                print(f'Dropped {num_unseen} knockouts from input triples. See Output_dir/unseen_knockouts.tsv')

    # Calculate scores
    if args.query_type == 'sp_':
        subjects, predicates = prepare_sp_(input_triples, kge_model)
        query_scores = kge_model.score_sp(subjects, predicates).tolist()
    elif args.query_type == '_po':
        predicates, objects = prepare__po(input_triples, kge_model)
        query_scores = kge_model.score_po(predicates, objects).tolist()
    elif args.query_type == 's_o':
        subjects, objects = prepare_s_o(input_triples, kge_model)
        query_scores = kge_model.score_so(subjects, objects).tolist()
    else:
        raise ValueError(
            'Invalid query type, should be one of: "sp_", "_po", "s_o".')

    # Process and save results
    results = create_results_file(
        query_scores, kge_model, args.query_type)
    
    if args.addins:
        trimmed_results = input_triples[[0, 1, 2]]
        trimmed_results.columns = ['s', 'p', 'o']
        trimmed_results['addin'] = None
        trimmed_results['score'] = None
        element_type_to_check = [letter for letter in 'osp' if letter not in args.query_type][0]

        for i, row in trimmed_results.iterrows():
            element_to_check = row[element_type_to_check]
            score = results[element_to_check][i]
            trimmed_results['score'][i] = score

            trimmed_results['addin'][i] = [row['s'], row['p'], row['o']] in addins_list

        trimmed_results.to_csv(args.Output_loc + output_file_name, index=False)
    else:
        results.to_csv(args.Output_loc + output_file_name, index=False)

    # Store unseen knockouts if any exist
    try:
        if num_unseen > 0:
            unseen_knockouts.to_csv(args.Output_loc + '/unseen_knockouts.tsv', index=False, sep='\t')
    except NameError:
        pass