import networkx as nx
from louvain import get_neighbors_communities, remove_v_i, modularity_gain, hyper_graph
from math import exp
from random import choices
from typing import Any
import time


def leiden(G: nx.Graph) -> list[set[Any]]:
    # TODO: implement the algorithm similarly to louvain
    return [{None}]


def max_delta(
    G: nx.Graph, v_i: Any, neigh_communities: list[set[Any]], m: int
) -> tuple[int, float]:
    deltas = [modularity_gain(G, v_i, community, m) for community in neigh_communities]
    max_delta = max(deltas)
    return deltas.index(max_delta), max_delta


def move_nodes_fast(
    G: nx.Graph, communities: list[set[Any]], n_edges: int
) -> list[set[Any]]:
    Q: list[Any] = [G.nodes]
    while len(Q) != 0:
        v_i = Q.pop(0)
        max_index, max_delta = max_delta(G, v_i, communities, n_edges)
        if max_delta > 0:
            communities[max_index].add(v_i)
            neighbors = [
                neigh for neigh in G[v_i] if neigh not in communities[max_index]
            ]
            # always append or only if not in Q? This needs to be verified
            Q.append(neighbors)

    return communities


def refine_communities(G: nx.Graph, communities: list[set[Any]]) -> list[set[Any]]:
    refined_comms: list[set[Any]] = [{x} for x in G.nodes()]
    for comm in communities:
        refined_comms = merge_nodes_subset(G, refined_comms, comm)
    return refined_comms


def merge_nodes_subset(
    G: nx.Graph, communities: list[set[Any]], subset: set[Any]
) -> list[set[Any]]:
    # clojure: function in a function
    def connected_measure(comm_1, comm_2):
        return sum(
            [wt for _, v, wt in G.edges(n, data="weight", default=1) if v in comm]
        )

    well_connected_nodes: list[Any] = [
        v for v in subset if connected_measure(v, subset - {v}) >= (len(subset) - 1)
    ]

    for v in well_connected_nodes:
        # get the community to which v belongs to
        comm_v = [comm for comm in communities if v in comm][0]
        if len(comm_v) == 1:
            # consider only well connected communities
            well_connected_comms: list[set] = [
                comm
                for comm in communities
                if comm.issubset(subset)
                and connected_measure(comm, subset - comm)
                > len(comm) * (len(subset) - len(comm))
            ]
            # generate probabilities for each considered community
            proba_comms = []
            for comm in well_connected_comms:
                mod = modularity_gain(G, v, comm, len(G.edges()))
                if mod >= 0:
                    proba_comms.append(exp(1 / 2 * mod))
                else:
                    proba_comms.append(0)

            # necessary to unpack the list returned by choices()
            [selected_comm] = choices(well_connected_comms, proba_comms, k=1)
            selected_comm.add(v)

    return communities


# Graph Example from the lecture slides
edgelist = [
    (0, 2),
    (0, 3),
    (0, 4),
    (0, 5),
    (1, 2),
    (1, 4),
    (1, 7),
    (2, 4),
    (2, 5),
    (2, 6),
    (3, 7),
    (4, 10),
    (5, 7),
    (5, 11),
    (6, 7),
    (6, 11),
    (8, 9),
    (8, 10),
    (8, 11),
    (8, 14),
    (8, 15),
    (9, 12),
    (9, 14),
    (10, 11),
    (10, 12),
    (10, 13),
    (10, 14),
    (11, 13),
]

toy_graph = [
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 2),
    (1, 3),
    (2, 4),
]

G = nx.Graph(toy_graph)
start = time.time()
final_communities = leiden(G)
stop = time.time()
print("Number of communities:", len(final_communities))
print("Wall clock time", stop - start)
