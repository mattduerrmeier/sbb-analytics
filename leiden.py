from louvain import get_neighbors_communities, remove_v, modularity_gain, hyper_graph
import networkx as nx
from math import exp
from random import choices
import time
from typing import TypeVar
import copy
import random
import operator

T = TypeVar("T")

"""
This is an incomplete implementation of the Leiden algorithm.
Unfortunately we were not able to finish it.
There are still a few issues with the implementation.
"""


def leiden(G: nx.Graph) -> list[set[T]]:
    G.add_weighted_edges_from(G.edges(data="weight", default=1))
    m = len(G.edges())
    communities: list[set[T]] = [{v} for v in G.nodes()]

    done = False
    while not done:
        communities = move_nodes_fast(G, communities, m)
        if len(G.nodes) == len(communities) or len(communities) <= 2:
            done = True
        if not done:
            communities_refined = refine_communities(G, communities)
            G = hyper_graph(G, communities_refined)
            communities = [{v for v in C if v in G.nodes} for C in communities]
    return communities


def max_delta(
    G: nx.Graph, v: T, neigh_communities: list[set[T]], m: int
) -> tuple[int, float]:
    deltas = [modularity_gain(G, v, community, m) for community in neigh_communities]
    max_delta = max(deltas)
    return deltas.index(max_delta), max_delta


def move_nodes_fast(
    G: nx.Graph, communities: list[set[T]], n_edges: int
) -> list[set[T]]:
    Q = list(G.nodes)
    while len(Q) != 0:
        v = Q.pop(0)
        start_comm = copy.deepcopy(communities)
        for i, comm in enumerate(communities):
            if v in comm:
                communities[i].remove(v)
                if len(comm) == 0:
                    communities.remove(comm)
                break
        max_index, delta = max_delta(G, v, communities, n_edges)
        if delta > 0:
            communities[max_index].add(v)
            if start_comm != communities:
                for neighbor in G.neighbors(v):
                    if neighbor not in communities[max_index] and neighbor not in Q:
                        Q.append(neighbor)

    return communities


def refine_communities(G: nx.Graph, communities: list[set[T]]) -> list[set[T]]:
    refined_comms: list[set[T]] = [{v} for v in G.nodes()]
    for comm in communities:
        refined_comms = merge_nodes_subset(G, refined_comms, comm)
    return refined_comms


def merge_nodes_subset(
    G: nx.Graph, communities: list[set[T]], subset: set[T]
) -> list[set[T]]:
    # clojure: function in a function
    def connected_measure(comm_1: T | set[T], comm_2: set[T]) -> int:
        return sum(
            [
                wt
                for _, v, wt in G.edges(comm_1, data="weight", default=1)
                if v in comm_2
            ]
        )

    well_connected_nodes = [
        v for v in subset if connected_measure(v, subset - {v}) >= (len(subset) - 1)
    ]
    # Visit nodes in random order
    random.shuffle(well_connected_nodes)
    for v in well_connected_nodes:
        # consider only nodes that have not yet been merged
        if {v} in communities:
            # consider only well-connected communities
            well_connected_comms: list[set[T]] = [
                comm
                for comm in communities
                if comm.issubset(subset)
                and connected_measure(comm, subset - comm)
                > len(comm) / 7 * (len(subset) - len(comm))
            ]

            if len(well_connected_comms) > 0:
                # generate probabilities for each considered community
                proba_comms = []
                for comm in well_connected_comms:
                    mod = modularity_gain(G, v, comm, len(G.edges()))
                    if mod >= 0:
                        proba_comms.append(exp(10 * mod))
                    else:
                        proba_comms.append(0)

                # necessary to unpack the list returned by choices()
                if max(proba_comms) == 0:
                    [selected_comm] = choices(well_connected_comms, k=1)
                else:
                    [selected_comm] = choices(well_connected_comms, proba_comms, k=1)

                selected_comm.add(v)
                if len(selected_comm) != 1:
                    communities.remove({v})
    return communities
