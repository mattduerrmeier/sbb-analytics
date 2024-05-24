import networkx as nx
from typing import TypeVar

T = TypeVar("T")


# consumes the generator until the very last iteration
def louvain_implementation(graph: nx.Graph) -> list[set[T]]:
    comp = louvain_generator(graph)
    final_communities = None
    for com in comp:
        final_communities = com

    return final_communities


def louvain_generator(g: nx.Graph) -> list[set[T]]:
    threshold = 0.001
    g.add_weighted_edges_from(g.edges(data="weight", default=1))
    m = len(g.edges())

    # creates communities until convergence.
    communities, _ = step_1(g, m, True)
    yield communities

    node2com = {n: n for n in g.nodes}

    # instantiation of list
    list_of_modularity = [threshold]
    while max(list_of_modularity) >= threshold:
        # 5: create hypergraph & repeat step 1 until convergence or modularity is lower than threshold.
        g_hyper, node2com = hyper_graph(g, communities, node2com)
        communities, list_of_modularity = step_1(g_hyper, m, False)
        yield rebuild_communities(node2com, communities)
    return rebuild_communities(node2com, communities)


def step_1(g, m, passage_1):
    list_of_modularity = []
    # 1: init each node as a community
    communities: list[set[T]] = [{v} for v in g.nodes()]
    evolved = True
    while evolved:
        original_communities = communities.copy()
        for v in g.nodes():
            # 2: remove the node from its community
            communities, temp_com = remove_v(communities, v)

            neighbors_communities = get_neighbors_communities(
                g.neighbors(v), communities
            )
            # 3: add node to the community that maximizes delta
            highest_delta_community, gain = max_delta(g, v, neighbors_communities, m)
            highest_delta_community.add(v)

            if (highest_delta_community != temp_com) and passage_1 is False:
                list_of_modularity.append(gain)

        # 4: stop if process converges
        if original_communities == communities:
            evolved = False
    return communities, list_of_modularity


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
def max_delta(
    G: nx.Graph, v: T, neigh_communities: list[set[T]], m: int
) -> tuple[set[T], float]:
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
    g: nx.Graph, communities: list[set[T]], node2com: dict[T, int]
) -> tuple[nx.Graph, dict[T, int]]:
    new_g = nx.Graph()

    for i, com in enumerate(communities):
        new_g.add_node(i, nodes=com)

    for i in node2com:
        node2com[i] = node_to_which_community(communities, node2com[i])

    for u, v, wt in g.edges(data=True):
        com_1 = node2com[u]
        com_2 = node2com[v]
        temp_wt = new_g.get_edge_data(com_1, com_2, default={"weight": 0})
        new_g.add_edge(com_1, com_2, weight=wt["weight"] + temp_wt["weight"])

    return new_g, node2com


# tells to which community a node belongs to
def node_to_which_community(comm, elem):
    for id, com in enumerate(comm):
        if elem in com:
            return id


# keep track of which community each node is associated with. (useful when dealing with hypergraph)
def rebuild_communities(dict_of_node, comm):
    final_comm = []
    for _ in comm:
        final_comm.append([])

    for i in range(len(final_comm)):
        for node in dict_of_node:
            if dict_of_node[node] in comm[i]:
                final_comm[i].append(node)

    return [set(comm) for comm in final_comm]
