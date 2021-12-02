import networkx as nx
import pandas as pd
import numpy as np
import argparse
from os import listdir
from scipy import stats


def load_edgelist(data_path):

    if 'edgelist.tsv' in listdir(data_path):
        full_edgelist = pd.read_csv(data_path + '/edgelist.tsv', sep='\t', header=None)
    else:
        full_edgelist = pd.DataFrame()
        for split in ['train', 'test', 'valid']:
            split_edgelist = pd.read_csv(data_path + f'/{split}.txt', sep='\t', header=None)
            full_edgelist = full_edgelist.append(split_edgelist)
            
    full_edgelist.columns = ['s', 'p', 'o']
    return full_edgelist


def get_graph_stats(graph):

    stats_dict = {}
    stats_dict['num_nodes'] = len(graph.nodes)
    stats_dict['num_edges'] = len(graph.edges)

    degrees = [tup[1] for tup in graph.degree]
    stats_dict['mean_degree'] = np.mean(degrees)
    stats_dict['median_degree'] = np.median(degrees)
    stats_dict['max_degree'] = max(degrees)
    stats_dict['stdev_degree'] = np.std(degrees)
    stats_dict['skewness_degree'] = stats.skew(degrees)
    stats_dict['kurtosis_degree'] = stats.kurtosis(degrees)

    return stats_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gets attributes of given graph dataset')
    parser.add_argument('dataset_paths', nargs='+', metavar='G', type=str,
                        help='LibKGE datasets to analyse')
    args = parser.parse_args()

    # Load in datasets
    graphs = {}
    for path in args.dataset_paths:
        edgelist = load_edgelist(path)
        dataset_name = path.split('/')[-1]
        graphs[dataset_name] = edgelist

    # Create template output dataframe
    columns = [
        'graph_section',
        'num_nodes',
        'num_edges',
        'num_edge_types',
        'density',
        'mean_degree',
        'median_degree',
        'max_degree',
        'stdev_degree',
        'skewness_degree',
        'kurtosis_degree'
    ]
    
    # Iterate through graphs and get statistics
    for graph_name in graphs:
        target_edgelist = graphs[graph_name]
        output_df = pd.DataFrame(columns=columns)

        # Create multigraph
        edges_array = [(row.s, row.o, {'predicate': row.p}) for i, row in target_edgelist.iterrows()]
        target_graph = nx.MultiGraph()
        target_graph.add_edges_from(edges_array)
        assert len(target_edgelist) == len(target_graph.edges)

        # Analyse whole graph
        graph_stats = get_graph_stats(target_graph)
        graph_stats['num_edge_types'] = len(target_edgelist['p'].unique())
        graph_stats['density'] = graph_stats['num_edges'] / (graph_stats['num_nodes'] * (graph_stats['num_nodes']-1) * len(target_edgelist.p.unique()))
        row = pd.Series(graph_stats, index=columns)
        row.graph_section = 'full graph'
        output_df.loc[len(output_df)] = row

        # Analyse sections by meta-edge
        for predicate in target_edgelist.p.unique():

            # Extract subgraph
            subgraph_edges_array = [edge for edge in edges_array if edge[2]['predicate'] == predicate]
            target_subgraph = nx.MultiGraph()
            target_subgraph.add_edges_from(subgraph_edges_array)
            assert len(target_edgelist.loc[target_edgelist.p == predicate]) == len(target_subgraph.edges)

            # Analyse subgraph
            subgraph_stats = get_graph_stats(target_subgraph)
            subgraph_stats['num_edge_types'] = 1
            subgraph_stats['density'] = subgraph_stats['num_edges'] / (subgraph_stats['num_nodes'] * (subgraph_stats['num_nodes'] - 1))
            row = pd.Series(subgraph_stats, index=columns)
            row.graph_section = predicate
            output_df.loc[len(output_df)] = row

        # Save output in execution dir
        output_df.to_csv(f'attributes_{graph_name}.csv', index=False)
