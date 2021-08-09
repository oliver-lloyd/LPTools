from random import sample
import pandas as pd
import argparse

def get_nodelist(edgelist):

    s_nodes = list(edgelist[0].unique())
    o_nodes = list(edgelist[2].unique())
    all_nodes = pd.Series(s_nodes + o_nodes).unique()

    return all_nodes


def generate_new_edges(edgelist, addin_count, self_loops=False):

    # Get unique nodes and edges
    nodelist = list(get_nodelist(edgelist))
    meta_edges = list(edgelist[1].unique())

    # Generate new edges
    edges_list = [list(edge) for edge in edgelist.to_numpy()]  # Convert df to list of lists
    new_edges = []
    while len(new_edges) < addin_count:

        # Sample a candidate edge
        new_s = sample(nodelist, 1)[0]
        new_p = sample(meta_edges, 1)[0]
        new_o = sample(nodelist, 1)[0]
        if not self_loops:
            while new_s == new_o:
                new_o = sample(nodelist, 1)[0]
        new_edge = [new_s, new_p, new_o]

        # Check if edge is valid, store if it is, skip otherwise
        if new_edge in edges_list:
            continue
        else:
            new_edges.append(new_edge)

    return new_edges


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add randomly selected edges into an edge list')
    parser.add_argument('Edgelist', metavar='E', type=str,
                        help='Edge list to process')
    parser.add_argument('Num_addins', metavar='N', type=int,
                        help='Number of novel edges to add in')
    parser.add_argument('--allow_self_loops', metavar='s', type=bool, default=False,
                        help='Whether to allow edges where s == o')
    args = parser.parse_args()

    # Read in edgelist
    edges = pd.read_csv(args.Edgelist, header=None, sep='\t')

    # Randomly generate novel edges
    edges_to_add = generate_new_edges(edges, args.Num_addins, args.allow_self_loops)

    # Parse output loc
    if '/' in args.Edgelist:
        path = args.Edgelist.split('/')
        output_dir = '/'.join(path[:-1]) + '/'
        edgelist_file_name = path[-1]
    else:
        output_dir = ''
        edgelist_file_name = args.Edgelist

    # Add new edges and save
    addins = pd.DataFrame(edges_to_add)
    edgelist_with_addins = edges.append(addins)

    edgelist_with_addins.to_csv(output_dir + edgelist_file_name[:-4] + f'_added_in_{args.Num_addins}.tsv', header=False, index=False, sep='\t')
    addins.to_csv(output_dir + f'{args.Num_addins}_addins.tsv', header=False, index=False, sep='\t')
    