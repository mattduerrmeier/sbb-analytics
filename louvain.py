import networkx as nx
import time
from typing import TypeVar

T = TypeVar("T")


# consumes the generator until the very last iteration
def louvain_implementation(G: nx.Graph) -> list[set[T]]:
    comp = louvain_generator(G)
    final_communities = None
    for com in comp:
        final_communities = com

    return final_communities


def louvain_generator(G: nx.Graph) -> list[set[T]]:
    threshold = 0.001
    G.add_weighted_edges_from(G.edges(data="weight", default=1))
    m = len(G.edges())
    # 1: init each node as a community
    communities: list[set[T]] = [{v} for v in G.nodes()]
    evolved = True
    while evolved:
        original_communities = communities.copy()
        for v in G.nodes():
            # 2: remove the node from its community
            communities, temp_comp = remove_v(communities, v)

            neighbors_communities = get_neighbors_communities(
                G.neighbors(v), communities
            )
            # 3: add node to the community that maximizes delta
            highest_delta_community, gain = max_delta(G, v, neighbors_communities, m)
            highest_delta_community.add(v)

        # 4: stop if process converges
        if original_communities == communities:
            evolved = False

    yield communities

    node2com = {n: n for n in G.nodes}
    list_of_modularity = [threshold]
    # 5: create hypergraph

    while max(list_of_modularity) >= threshold:
        list_of_modularity = []

        G_hyper, node2com = hyper_graph(G, communities, node2com)
        communities = [{v} for v in G_hyper.nodes()]
        evolved = True
        while evolved:
            original_communities = communities.copy()
            for v in G_hyper.nodes():
                # 2: remove the node from its community
                communities, temp_com = remove_v(communities, v)
                neighbors_communities = get_neighbors_communities(
                    G_hyper.neighbors(v), communities
                )
                # 3: add node to the community that maximizes delta
                highest_delta_community, gain = max_delta(G_hyper, v, neighbors_communities, m)
                highest_delta_community.add(v)

                if highest_delta_community != temp_com:
                    list_of_modularity.append(gain)
            # stop if process converges or remaining 2 communities
            if original_communities == communities:
                evolved = False
            yield rebuild_communities(node2com, communities)

    return rebuild_communities(node2com, communities)


# TODO: Improve this function. How can we get the neighbors without the nested for loop?
# returns all communities adjacent to the node
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
def remove_v(communities: list[set[T]], v: T) -> tuple[list[set[T]], set[T]]:
    temp_com = None
    for com in communities:
        if v in com:
            temp_com = com.copy()
            com.remove(v)
            # if the set is empty we should remove it
            if len(com) == 0:
                communities.remove(com)
            break
    return communities, temp_com

# keep the highest modularity gain
def max_delta(G: nx.Graph, v: T, neigh_communities: list[set[T]], m: int) -> tuple[set[T], float]:
    deltas = [modularity_gain(G, v, community, m) for community in neigh_communities]
    return neigh_communities[deltas.index(max(deltas))], max(deltas)

# compute modularity gain between a node and a community
def modularity_gain(G: nx.Graph, v: T, community: set[T], m: int) -> float:
    # creating the dict once is faster than accessing the degrees twice
    degrees = dict(G.degree(community | {v}, weight="weight"))

    d_ij = 2 * sum(
        [wt for _, w, wt in G.edges(v, data="weight", default=1) if w in community]
    )
    d_i = degrees[v]
    d_j = sum([degrees[n] for n in community])

    return 1 / (2 * m) * (d_ij - (d_i * d_j) / m)


# merging all nodes within a community into a hypernode.
def hyper_graph(
    G: nx.Graph, communities: list[set[T]], node2com: dict[T, int]
) -> tuple[nx.Graph, dict[T, int]]:
    new_G = nx.Graph()

    for i, com in enumerate(communities):
        new_G.add_node(i, nodes=com)

    for i in node2com:
        node2com[i] = node_to_which_community(communities, node2com[i])
    for u, v, wt in G.edges(data=True):
        com_1 = node2com[u]
        com_2 = node2com[v]

        temp_wt = new_G.get_edge_data(com_1, com_2, default={"weight": 0})
        new_G.add_edge(com_1, com_2, weight=wt["weight"] + temp_wt["weight"])
    return new_G, node2com

# tells to which community a node belongs to
def node_to_which_community(comm, elem):
    for id, com in enumerate(comm):
        if elem in com:
            return id

# keep track of which community each node is associated with. (useful when dealing with hypergraph)
def rebuild_communities(dict_of_node, commu):
    final_comm = []
    for _ in commu:
        final_comm.append([])

    for i in range(len(final_comm)):
        for node in dict_of_node:
            if dict_of_node[node] in commu[i]:
                final_comm[i].append(node)

    return [set(comm) for comm in final_comm]


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
G = nx.read_edgelist("data/sbb.edgelist", delimiter=";", create_using=nx.Graph)
connected_comp = nx.connected_components(G)
max_connected_comp = max(connected_comp)
sub_G = G.subgraph(max_connected_comp)
G = nx.Graph(sub_G)

final_communities = louvain_implementation(G)
print(len(final_communities), final_communities)
#print("Generator: ", len(final_communities))
# print(count)
# #gen = louvain_generator(G)
