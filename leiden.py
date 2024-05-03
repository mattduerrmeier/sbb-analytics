import networkx as nx
import time
from typing import Any, Tuple, Set


def leiden(G: nx.Graph) -> list[set[Any]]:
    G.add_weighted_edges_from(G.edges(data="weight", default=1))
    m = len(G.edges())
    # 1: init each node as a community
    communities: list[set[Any]] = [{x} for x in G.nodes()]

    evolved = True
    while evolved:
        original_communities = communities.copy()
        for v_i in G.nodes():
            # 2: remove the node from its community
            communities = rm_vi_from_its_community(communities, v_i)

            neighbors_communities = get_neighbors_communities(
                G.neighbors(v_i), communities
            )
            # 3: add node to the community that maximizes delta
            highest_delta_community = max_delta(G, {v_i}, neighbors_communities, m)
            highest_delta_community.add(v_i)

        # 4: stop if process converges
        if original_communities == communities:
            evolved = False

    # 5: create hypergraph
    G_hyper = hyper_graph(G, communities)
    communities: list[set[Any]] = [{x} for x in G_hyper.nodes()]

    evolved_new = True
    while evolved_new:
        original_communities = communities.copy()
        for v_i in G_hyper.nodes():
            # 2: remove the node from its community
            communities = rm_vi_from_its_community(communities, v_i)
            neighbors_communities = get_neighbors_communities(
                G_hyper.neighbors(v_i), communities
            )
            # 3: add node to the community that maximizes delta
            # TODO: create other function to calculate highest
            highest_delta_community = max_delta_hypergraph(
                G_hyper, {v_i}, neighbors_communities, m
            )
            highest_delta_community[0].add(v_i)

        if original_communities == communities:
            evolved_new = False

    return communities


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


# Step 2: remove (v_i) from its community
def rm_vi_from_its_community(communities: list[set[Any]], v_i: Any) -> list[set[Any]]:
    removed = False
    counter = 0
    while removed == False:
        if v_i in communities[counter]:
            communities[counter].remove(v_i)
            if len(communities[counter]) == 0:
                del communities[counter]

            removed = True
        else:
            counter += 1

    return communities


def max_delta(
    G: nx.Graph, community_1: set[Any], neigh_communities: list[set[Any]], m: int
) -> set[Any]:
    deltas = [
        modularity_gain(G, community_1, community_2, m)
        for community_2 in neigh_communities
    ]
    return neigh_communities[deltas.index(max(deltas))]


def max_delta_hypergraph(
    G: nx.Graph, community_1: set[Any], neigh_communities: list[set[Any]], m: int
) -> tuple[set[Any], float]:
    deltas = [
        modularity_gain_hyper(G, community_1, community_2, m)
        for community_2 in neigh_communities
    ]
    return neigh_communities[deltas.index(max(deltas))], max(deltas)


def modularity_gain(
    G: nx.Graph, community_1: set[Any], community_2: set[Any], m: int
) -> float:
    d_ij = shared_degree(G, community_1, community_2)
    d_i = sum([G.degree(n) for n in community_1])
    d_j = sum([G.degree(n) for n in community_2])

    r = 1 / (2 * m)
    l = d_ij - (d_i * d_j) / m
    return r * l


def modularity_gain_hyper(
    G: nx.Graph, community_1: set[Any], community_2: set[Any], m: int
) -> float:
    d_ij = 0
    d_i = 0
    for n in community_1:
        for _, n2, wt in G.edges(n, data=True):
            d_i += wt["weight"]
            if n2 in community_2:
                d_ij += wt["weight"]
    d_ij = d_ij * 2

    d_j = 0
    for n in community_2:
        for _, _, wt in G.edges(n, data=True):
            d_j += wt["weight"]

    r = 1 / (2 * m)
    l = d_ij - (d_i * d_j) / m
    return r * l


def shared_degree(G: nx.Graph, community_1: set[Any], community_2: set[Any]) -> int:
    # do we need to remove duplicates?
    neighbors_comm_1 = [neigh for n in community_1 for neigh in G[n]]
    d_ij = [neigh for neigh in neighbors_comm_1 if neigh in community_2]
    return 2 * len(d_ij)


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


def move_nodes_fast(G, communities, n_edges):
    Q = [G.nodes]
    while len(Q) != 0:
        vi = Q.pop()
        max_index, max_delta = max_delta_hypergraph(G, set(vi), communities, n_edges)
        if max_delta > 0:
            communities[max_index].add(vi)
            neighbors = G.neighbors(vi)
            for neighbor in neighbors:
                if neighbor not in Q and neighbor not in communities[max_index]:
                    Q.append(neighbors)
    return communities


def refine_partitions(G, communities):
    singleton_partitions: list[set[Any]] = [{x} for x in G.nodes()]
    for sub in communities:
        partition_refined = merge_nodes_subset(G, communities, singleton_partitions)
    return partition_refined


def merge_nodes_subset(G, communities, subset):
    R = [v_i for v_i in subset if
         len([G.has_edges(v_i, incident) for incident in [x for (y, x) in test_G.edges(v_i) ]]) >=
         G.degree(v_i) * (sum([G.degree(x) for x in subset]) - G.degree(v_i))]
    for vi in R:
        l_mod_gain = []
        if modularity_gain_hyper(G, vi, subset, len(G.edges)) > 0:
            l_mod_gain.append(modularity_gain_hyper(G, vi, subset, len(G.edges)))



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

# G = nx.read_edgelist("./sbb.edgelist", delimiter=";", create_using=nx.Graph)
# connected_comp = nx.connected_components(G)
# max_connected_comp = max(connected_comp)
# print("Number of nodes in largest connected component:", len(max_connected_comp))
#
# sub_G = nx.Graph(G.subgraph(max_connected_comp))

test_G = nx.Graph(edgelist)


leiden(test_G)
start = time.time()
final_communities = leiden(test_G)
stop = time.time()
print("Number of communities:", len(final_communities))
print("Wall clock time", stop - start)