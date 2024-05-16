import networkx as nx
import time
from typing import TypeVar

T = TypeVar("T")


def louvain(G: nx.Graph) -> list[set[T]]:
    G.add_weighted_edges_from(G.edges(data="weight", default=1))
    m = len(G.edges())
    # 1: init each node as a community
    communities: list[set[T]] = [{v} for v in G.nodes()]

    evolved = True
    while evolved:
        original_communities = communities.copy()
        for v in G.nodes():
            # 2: remove the node from its community
            communities = remove_v(communities, v)

            neighbors_communities = get_neighbors_communities(
                G.neighbors(v), communities
            )
            # 3: add node to the community that maximizes delta
            highest_delta_community = max_delta(G, v, neighbors_communities, m)
            highest_delta_community.add(v)

        # 4: stop if process converges
        if original_communities == communities:
            evolved = False

    # 5: create hypergraph
    G_hyper = hyper_graph(G, communities)
    communities = [{v} for v in G_hyper.nodes()]

    evolved = True
    while evolved:
        original_communities = communities.copy()
        for v in G_hyper.nodes():
            # 2: remove the node from its community
            communities = remove_v(communities, v)
            neighbors_communities = get_neighbors_communities(
                G_hyper.neighbors(v), communities
            )
            # 3: add node to the community that maximizes delta
            highest_delta_community = max_delta(G_hyper, v, neighbors_communities, m)
            highest_delta_community.add(v)

        if original_communities == communities:
            evolved = False

    return communities


# TODO: Improve this function. How can we get the neighbors without the nested for loop?
def get_neighbors_communities(
    neighbors: list[T], communities: list[set[T]]
) -> list[set[T]]:
    neigh_communities = []

    all_neigh_communities = [
        comm for neigh in neighbors for comm in communities if neigh in comm
    ]
    for neigh in all_neigh_communities:
        if neigh not in neigh_communities:
            neigh_communities.append(neigh)

    return neigh_communities


# removes node v from its community
def remove_v(communities: list[set[T]], v: T) -> list[set[T]]:
    for com in communities:
        if v in com:
            com.remove(v)
            # if the set is empty we should remove it
            if len(com) == 0:
                communities.remove(com)
            break

    return communities


def max_delta(G: nx.Graph, v: T, neigh_communities: list[set[T]], m: int) -> set[T]:
    deltas = [modularity_gain(G, v, community, m) for community in neigh_communities]
    return neigh_communities[deltas.index(max(deltas))]


def modularity_gain(G: nx.Graph, v: T, community: set[T], m: int) -> float:
    # creating the dict once is faster than accessing the degrees twice
    degrees = dict(G.degree(community | {v}, weight="weight"))

    d_ij = 2 * sum(
        [wt for _, w, wt in G.edges(v, data="weight", default=1) if w in community]
    )
    d_i = degrees[v]
    d_j = sum([degrees[n] for n in community])

    return 1 / (2 * m) * (d_ij - (d_i * d_j) / m)


def hyper_graph(G: nx.Graph, communities: list[set[T]]) -> nx.Graph:
    new_G = nx.Graph()

    node2com: dict[T, int] = {}
    for i, com in enumerate(communities):
        new_G.add_node(i, nodes=com)
        for n in com:
            node2com[n] = i
    for u, v, wt in G.edges(data=True):
        com_1 = node2com[u]
        com_2 = node2com[v]

        temp_wt = new_G.get_edge_data(com_1, com_2, default={"weight": 0})
        new_G.add_edge(com_1, com_2, weight=wt["weight"] + temp_wt["weight"])

    return new_G

# TODO: return all nodes in communities, not the hypernodes
