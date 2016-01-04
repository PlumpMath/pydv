import networkx as nx

class Node:
    def __init__(self, name=None):
        self.name = name

class Graph:
    
    def __init__(self, name):
        self.name  = name
        self.graph = nx.DiGraph()

    def add_node(self, n):
        self.graph.add_node(n)

    def add_edge(self, n0, n1):
        self.graph.add_edge(n0, n1)

    def check_cycle(self):
        if not nx.is_directed_acyclic_graph(self.graph):
            raise Exception("attempt to add a cyclic")

    def subgraph(self, n):
        ns = nx.descendants(self.graph, n)
        return self.graph.subgraph(ns)

    def out_degree(self, n):
        return self.graph.out_degree(n)

    def nodes(self):
        return self.graph.nodes_iter()

    def successors(self, n):
        r = []
        for i in self.graph.successors_iter(n):
            r.append(i)
        return r

needgraph   = Graph('needgraph')
actiongraph = Graph('actiongraph')

