from random import sample
import pandas as pd
import argparse


def knockout(edge_list, knockout_index):
    knocked_out_edges = pd.DataFrame()
    for id in knockout_index:
        knocked_out_edges = knocked_out_edges.append(edge_list.loc[id])
        edge_list.drop(id, inplace=True)
    
    return edge_list, knocked_out_edges


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Randomly knockout edges from an edge list')
    parser.add_argument('Edgelist', metavar='E', type=str,
                        help='Edge list to process')
    parser.add_argument('--num_knockouts', metavar='N', type=int,
                        help='Number of edges to knockout. Default = 1% len(edgelist')
    args = parser.parse_args()

    # Read in edgelist
    edge_list = pd.read_csv(args.Edgelist, header=None, sep='\t')

    # Set indexes to knockout
    if args.num_knockouts:
        num_knocks = args.num_knockouts
        index_to_knockout = sample(list(edge_list.index.values), num_knocks)
    else:
        num_knocks = int(0.01 * len(edge_list))
        index_to_knockout = sample(list(edge_list.index.values), num_knocks)

    # Parse output loc
    if '/' in args.Edgelist:
        path = args.Edgelist.split('/')
        output_dir = '/'.join(path[:-1]) + '/'
        edgelist_file_name = path[-1]
    else:
        output_dir = ''
        edgelist_file_name = args.Edgelist

    # Do knockout and save
    remaining_edges, knockouts = knockout(edge_list, index_to_knockout)
    remaining_edges.to_csv(output_dir + edgelist_file_name[:-4] + f'_knocked_out_{num_knocks}.tsv', header=False, index=False, sep='\t')
    knockouts.to_csv(output_dir + f'{num_knocks}_knockouts.tsv', header=False, index=False, sep='\t')
    