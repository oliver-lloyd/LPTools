import networkx as nx
import argparse
import numpy as np
import pandas as pd

def get_degree_and_strength(g, node, directed=False):
    """
    For a given node in a network, returns node degree and node strength. 
    If network is directed, instead returns in-degree, in-strength, out-degree, and out-strength.
    """

    if directed:
        in_edges = []
        in_weights = []
        out_edges = []
        out_weights = []

        for edge in g.edges.data():
            if edge[0] == node:
                out_edges.append(edge[0])
                out_weights.append(edge[2]['weight'])
            elif edge[1] == node:
                in_edges.append(edge[1])
                in_weights.append(edge[2]['weight'])
        
        in_degree = len(in_edges)
        in_strength = np.median(in_weights)

        out_degree = len(out_edges)
        out_strength = np.median(out_weights)

        return [in_degree, in_strength, out_degree, out_strength]

    else:
        edges = [edge for edge in g.edges.data() if node in edge[]]
        degree = len(edges)
        weights = [edge[2]['weight'] for edge in edges]
        strength = np.median(weights)

        return [degree, strength]


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('edgelist_path')
    parser.add_argument('weight_variable')
    parser.add_argument('weight_transform', default=None)

    args = parser.parse_args()

    og_df = pd.read_csv(edgelist_path, header=None)

    if args.weight_transform == '-log10':
        og_df['weight'] = -np.log10(og_df[weight_variable])
    elif args.weight_transform == 'abs':
        og_df['weight'] = np.abs(og_df[weight_variable])
    elif args.weight_transform == None:
        og_df['weight'] = og_df[weight_variable]
    else:
        raise ValueError("Weight transform should be one of ['-log10', 'abs'] or left blank. ")

