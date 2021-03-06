import pickle

import networkx
from networkx.generators import cycle_graph, path_graph
from networkx.generators.atlas import graph_atlas_g

from isocket_settings import global_settings


class AtlasHandler:
    def __init__(self, mode='production'):
        self.mode = mode
        return

    @property
    def atlas_graphs(self):
        graph_list = graph_atlas_g()
        return graph_list

    @property
    def unknown_graphs(self):
        unknown_pickle = global_settings["unknown_graphs"][self.mode]
        try:
            with open(unknown_pickle, 'rb') as foo:
                graph_list = pickle.load(foo)
        except (FileNotFoundError, EOFError):
            graph_list = []
        return graph_list

    def cyclic_graphs(self, max_nodes):
        graph_list = []
        for n in range(8, max_nodes + 1):
            g = cycle_graph(n)
            g.name = 'C{}'.format(n)
            graph_list.append(g)
        return graph_list

    def path_graphs(self, max_nodes):
        graph_list = []
        for n in range(8, max_nodes + 1):
            g = path_graph(n)
            g.name = 'P{}'.format(n)
            graph_list.append(g)
        return graph_list

    def get_graph_list(self, atlas=True, cyclics=True, paths=False, unknowns=False, max_cyclics=100, max_paths=100):
        graph_list = []
        if atlas:
            graph_list = self.atlas_graphs
        if cyclics:
            graph_list += self.cyclic_graphs(max_nodes=max_cyclics)
        if paths:
            graph_list += self.path_graphs(max_nodes=max_paths)
        if unknowns:
            graph_list += self.unknown_graphs
        return graph_list


def graph_to_plain_graph(g):
    """ Convert complex (MultiDiGraph) into Graph, with integer nodes and tuple edges """
    # construct h fully in case of unorderable/unsortable edges.
    h = networkx.Graph()
    h.add_nodes_from(range(len(g.nodes())))
    edges = [(g.nodes().index(e1), g.nodes().index(e2)) for e1, e2 in g.edges()]
    h.add_edges_from(edges)
    h.graph['name'] = None
    return h


def isomorphism_checker(g, graph_list=None):
    """ Finds the name of the graph by checking for isomorphism with the graphs in the graph_list.

    Notes
    -----
    If g is a MultiGraph, a DiGraph or a MultiDiGraph, the isomorphism is run against the underlying Graph.
    In other words, all the edge annotations (including directions) are ignored.

    Parameters
    ----------
    g : A networkx Graph.
    graph_list :
        A list of networkx.Graph objects against which to check for isomorphism.
        If the graphs in the list do not have names, then their index will be returned as a string

    Returns
    -------
    iso_name : str, or None
        The name of the graph from the graph_list that is isomorphic to g.
        If the graph does not have a 'name' attribute, its index in the list will be returned as a string.
        None if no such isomorph is found in the list_of_graphs.

    """
    if graph_list is None:
        graph_list = graph_atlas_g()
    # run isomorphism check on the Graph of g (i.e. not the DiGraph or MultiGraph).
    h = graph_to_plain_graph(g)
    isomorph = next(filter(lambda x: networkx.is_isomorphic(h, x), graph_list), None)
    if isomorph is None:
        return
    else:
        iso_name = isomorph.name
        if iso_name is None:
            iso_name = str(graph_list.index(isomorph))
    return iso_name


def get_filtered_graph_list(atlas=True, cyclics=True, unknowns=False, paths=False, max_nodes=8,
                    min_nodes=2, max_degree=4, all_connected=True):
    """ Gets a square array of named graphs for use in atlas_visualisation.
    This is a temporary home for this function.
    Write the result of the array to a pickle file for use as basis of visualistaion.
    """
    graph_list = AtlasHandler().get_graph_list(atlas=atlas, cyclics=cyclics,
                                        unknowns=unknowns, paths=paths,
                                        max_cyclics=max_nodes, max_paths=max_nodes)
    graph_list = [g for g in graph_list if g.number_of_nodes() >= min_nodes]
    graph_list = [g for g in graph_list if g.number_of_nodes() <= max_nodes]
    if all_connected:
        graph_list = [g for g in graph_list if networkx.connected.is_connected(g)]
    graph_list = [g for g in graph_list if max(g.degree().values()) <= max_degree]
    return graph_list


__author__ = 'Jack W. Heal'
