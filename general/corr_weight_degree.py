import networkx as nx
import argparse
import numpy as np
import pandas as pd
import multiprocessing as mp
from scipy.stats import pearsonr
from datetime import datetime

def get_degree_and_strength(g, node, directed=False):
    """
    For a given node in a network, returns node degree and node strength. 
    If network is directed, instead returns in-degree, in-strength, out-degree, and out-strength.
    """

    if directed:
        in_degree = 0
        in_weights = []
        out_degree = 0
        out_weights = []

        edges = set(list(g.edges(node)) + list(g.in_edges(node)))
        for edge in edges:
            weight = g.get_edge_data(*edge)['weight']
            if edge[0] == node:
                out_degree += 1
                out_weights.append(weight)
            elif edge[1] == node:
                in_degree += 1
                in_weights.append(weight)

        
        if len(in_weights) == 0: # Account for edges with no in/out 
            in_strength = 0
        else:
            in_strength = np.median(in_weights)
            if in_strength == np.inf:
                print(node, in_weights)
        if len(out_weights) == 0:
            out_strength = 0
        else:
            out_strength = np.median(out_weights)

        return [node, in_degree, in_strength, out_degree, out_strength]

    else:
        edges = g.adj[node]
        degree = len(edges)
        if len(edges) == 0:
            strength = 0
        else:
            weights = [edge['weight'] for edge in edges]
            strength = np.median(weights)

        return [node, degree, strength]


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('edgelist_path', type=str)
    parser.add_argument('head_node')
    parser.add_argument('tail_node')
    parser.add_argument('directed', type=bool)
    parser.add_argument('weight_variable', type=str)
    parser.add_argument('weight_transform', type=str)
    args = parser.parse_args()

    # Read in data
    df = pd.read_csv(args.edgelist_path)

    # Transform weight variable
    if args.weight_transform == 'neglog10':
        df['weight'] = -np.log10(df[args.weight_variable])
    elif args.weight_transform == 'abs':
        df['weight'] = np.abs(df[args.weight_variable])
    elif args.weight_transform == None:
        df['weight'] = df[args.weight_variable]
    else:
        raise ValueError("Weight transform should be one of ['-log10', 'abs'] or left blank. ")

    # Remove edges with no weight info
    raw_num_edges = len(df)
    df = df.loc[pd.notna(df.weight)]
    no_weight_edges = raw_num_edges - len(df)

    # Parse head and tail node arguments (they can be column index or str)
    try:
        head_ind = int(args.head_node)
        head = df.columns[head_ind]
    except ValueError:
        head = args.head_node
    try:
        tail_ind = int(args.tail_node)
        tail = df.columns[tail_ind]
    except ValueError:
        tail = args.tail_node
    
    # Create graph
    graph_directed = {True: nx.DiGraph, False: nx.Graph()}
    g = nx.from_pandas_edgelist(df, head, tail, edge_attr='weight', create_using=graph_directed[args.directed])
    assert len(df) == len(g.edges())
    del df

    # Get weights and degrees in parallel
    func_args = [[g, node, args.directed] for node in g.nodes()]
    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.starmap(get_degree_and_strength, func_args)
    del g

    # Create output df
    output_df = pd.DataFrame(results)
    if args.directed:
        output_df.columns = ['node', 'in_degree', 'in_strength', 'out_degree', 'out_strength']
    else:
        output_df.columns = ['node', 'degree', 'strength']

    now = str(datetime.now())[:19].replace(' ', '_')
    output_df.to_csv(f'weight_degree_data_{now}.csv', index=False)


    # Calculate correlations and write summary file 
    with open(f'weight_degree_summary_{now}.txt', 'w+') as f:
        f.write(f'Summary for weight-degree correlation analysis of dataset {args.edgelist_path}:\n')
        f.write(f'Raw data had {raw_num_edges} edges, removed {no_weight_edges} due to lack of weight info.\n')
        if args.directed:
            in_corr = pearsonr(output_df['in_degree'], output_df['in_strength'])
            out_corr = pearsonr(output_df['out_degree'], output_df['out_strength'])
            f.write(f'- In-weight-degree correlation: r={in_corr[0]} with pval={in_corr[1]}\n')
            f.write(f'- Out-weight-degree correlation: r={out_corr[0]} with pval={out_corr[1]}')
        else:
            corr = pearsonr(output_df['degree'], output_df['strength'])
            f.write(f'- Weight-degree correlation: r={corr[0]} with pval={corr[1]}')

