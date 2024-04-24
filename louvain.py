import networkx as nx
from typing import Any


def louvain(G: nx.Graph) -> list[set[Any]]:
    m = len(G.edges())
    # 1: init each node as a community
    communities: list[set[Any]] = [{x} for x in sorted(G.nodes())]

    evolved = True
    while evolved:
        original_communities = communities.copy()
        for v_i in sorted(G.nodes()):
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

    # 5: TODO: create hypernodes

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


def modularity_gain(
    G: nx.Graph, community_1: set[Any], community_2: set[Any], m: int
) -> float:
    d_ij = shared_degree(G, community_1, community_2)

    d_i = sum([G.degree(n) for n in community_1])
    d_j = sum([G.degree(n) for n in community_2])

    r = 1 / (2 * m)
    l = d_ij - (d_i * d_j) / m
    return r * l


def shared_degree(G: nx.Graph, community_1: set[Any], community_2: set[Any]) -> int:
    # do we need to remove duplicates?
    neighbors_comm_1 = [neigh for n in community_1 for neigh in G[n]]
    d_ij = [neigh for neigh in neighbors_comm_1 if neigh in community_2]
    return 2 * len(d_ij)


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

G = nx.Graph(edgelist)
comms = louvain(G)
