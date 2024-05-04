import networkx as nx
import time
from typing import Any


def louvain(G: nx.Graph) -> list[set[Any]]:
    G.add_weighted_edges_from(G.edges(data="weight", default=1))
    m = len(G.edges())
    # 1: init each node as a community
    communities: list[set[Any]] = [{x} for x in G.nodes()]

    evolved = True
    while evolved:
        original_communities = communities.copy()
        for v_i in G.nodes():
            # 2: remove the node from its community
            communities = remove_v_i(communities, v_i)

            neighbors_communities = get_neighbors_communities(
                G.neighbors(v_i), communities
            )
            # 3: add node to the community that maximizes delta
            highest_delta_community = max_delta(G, v_i, neighbors_communities, m)
            highest_delta_community.add(v_i)

        # 4: stop if process converges
        if original_communities == communities:
            evolved = False

    # 5: create hypergraph
    G_hyper = hyper_graph(G, communities)
    communities = [{x} for x in G_hyper.nodes()]

    evolved = True
    while evolved:
        original_communities = communities.copy()
        for v_i in G_hyper.nodes():
            # 2: remove the node from its community
            communities = remove_v_i(communities, v_i)
            neighbors_communities = get_neighbors_communities(
                G_hyper.neighbors(v_i), communities
            )
            # 3: add node to the community that maximizes delta
            highest_delta_community = max_delta(G_hyper, v_i, neighbors_communities, m)
            highest_delta_community.add(v_i)

        if original_communities == communities:
            evolved = False

    return communities


# TODO: Improve this function. How can we get the neighbors without the nested for loop?
def get_neighbors_communities(
    neighbors: list[Any], communities: list[set[Any]]
) -> list[Any]:
    neigh_communities = []

    all_neigh_communities = [
        comm for neigh in neighbors for comm in communities if neigh in comm
    ]
    for neigh in all_neigh_communities:
        if neigh not in neigh_communities:
            neigh_communities.append(neigh)

    return neigh_communities


# removes v_i from its community
def remove_v_i(communities: list[set[Any]], v_i: Any) -> list[set[Any]]:
    for com in communities:
        if v_i in com:
            com.remove(v_i)
            # if the set is empty we should remove it
            if len(com) == 0:
                communities.remove(com)
            break

    return communities


def max_delta(
    G: nx.Graph, v_i: Any, neigh_communities: list[set[Any]], m: int
) -> set[Any]:
    deltas = [modularity_gain(G, v_i, community, m) for community in neigh_communities]
    return neigh_communities[deltas.index(max(deltas))]


def modularity_gain(G: nx.Graph, v_i: Any, community: set[Any], m: int) -> float:
    # creating the dict once is faster than accessing the degrees twice
    degrees = dict(G.degree(community | {v_i}, weight="weight"))

    d_ij = 2 * sum(
        [wt for _, v, wt in G.edges(v_i, data="weight", default=1) if v in community]
    )
    d_i = degrees[v_i]
    d_j = sum([degrees[n] for n in community])

    return 1 / (2 * m) * (d_ij - (d_i * d_j) / m)


def hyper_graph(G: nx.Graph, communities: list[set[Any]]) -> nx.Graph:
    new_G = nx.Graph()

    node2com = {}
    for i, com in enumerate(communities):
        new_G.add_node(i, nodes=com)
        for n in com:
            node2com[n] = i

    for n1, n2, wt in G.edges(data=True):
        com1 = node2com[n1]
        com2 = node2com[n2]

        temp_wt = new_G.get_edge_data(com1, com2, default={"weight": 0})
        new_G.add_edge(com1, com2, weight=wt["weight"] + temp_wt["weight"])

    return new_G


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
