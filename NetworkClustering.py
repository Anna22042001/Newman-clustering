import sys
import Dijkstra
import Graph
import csv
import random
import copy


class NewmanClustering:

    def __init__(self):
        pass

    def performNewmanClustering(self, graph, K):
        lstVertexes = graph.vertexes

        print("-------------------------------")
        print("Initial Dataset")
        graph.printComponent()

        cnt = 0
        while True:
            # Compute the edge-betweenness
            matBetweenness = self.calculateEdgeBetweenness(graph)
            maxBetweenness = 0.0
            idxSrcEdge = -1
            idxDstEdge = -1

            for itr1 in range(len(lstVertexes)):
                for itr2 in range(len(lstVertexes)):
                    if matBetweenness[lstVertexes[itr1]][lstVertexes[itr2]] > maxBetweenness:
                        maxBetweenness = matBetweenness[lstVertexes[itr1]][lstVertexes[itr2]]
                        idxSrcEdge = itr1
                        idxDstEdge = itr2

                    # Remove the edge with the maximum edge-betweenness
            graph.removeEdge(lstVertexes[idxSrcEdge], lstVertexes[idxDstEdge])
            graph.removeEdge(lstVertexes[idxDstEdge], lstVertexes[idxSrcEdge])
            components = graph.findComponent()
            print("-------------------------------")
            print("Iteration " + str(cnt))
            graph.printComponent()
            if len(components) == K:
                return components
                break
            cnt = cnt + 1

    def calculateEdgeBetweenness(self, graph):
        lstVertexes = graph.vertexes
        matBetweenness = {}
        for itr1 in range(len(lstVertexes)):
            matBetweenness[lstVertexes[itr1]] = {}
            for itr2 in range(len(lstVertexes)):
                matBetweenness[lstVertexes[itr1]][lstVertexes[itr2]] = 0.0

        print("Calculating Betweenness ")
        for itr1 in range(len(lstVertexes)):
            print(".", end="")
            sys.stdout.flush()
            dist, path, routes = Dijkstra.performAllDestinationDijkstra(graph, lstVertexes[itr1])
            for itr2 in range(len(lstVertexes)):
                if itr1 == itr2:
                    continue

                # Remember that "routes" is a dictionary with a string key as a station name
                # lstVertexes[itr1] is the source
                # lstVertexes[itr2] is the destination
                # routes[lstVertexes[itr2] is the list of the station in the path between the source and the destination
                # You need to increase the matrix of the edge-betweenness
                if routes[lstVertexes[itr2]] != None:
                    for itr3 in range(len(routes[lstVertexes[itr2]]) - 1):
                        srcIncludedEdge = routes[lstVertexes[itr2]][itr3]
                        dstIncludedEdge = routes[lstVertexes[itr2]][itr3 + 1]
                        matBetweenness[srcIncludedEdge][dstIncludedEdge] = matBetweenness[srcIncludedEdge][
                                                                               dstIncludedEdge] + 1
                        matBetweenness[dstIncludedEdge][srcIncludedEdge] = matBetweenness[dstIncludedEdge][
                                                                               srcIncludedEdge] + 1
        print()
        return matBetweenness


class Node:
    def __init__(self, value, father, mother):
        self.value = value
        self.child = []
        self.father = father
        self.depth = 0
        self.mother = mother

    def getValue(self):
        return self.value

    def addChild(self):
        self.child = []
        for neighbor in self.mother.edges[self.value].keys():
            if self.father is None or neighbor != self.father.value:
                child = Node(neighbor, self, self.mother)
                child.addChild()
                self.child.append(child)

    def setDepth(self):
        if len(self.child) == 0:
            return 0
        max_dis = -9999
        for child in self.child:
            child_dis = self.mother.edges[self.value][child.value] + child.setDepth()
            if child_dis > max_dis:
                max_dis = child_dis
        self.depth = max_dis
        return max_dis

    def getString(self, depth):
        ret = ""
        for itr in range(depth):
            ret = ret + "...."
        ret = ret + str(self.value) + "\n"
        for child in self.child:
            ret = ret + child.getString(depth + 1)
        return ret


def balance(root):
    current = root
    current_Depth = current.depth
    while True:
        max_sub = -1
        max_child = None
        for child in current.child:
            subdepth = child.depth
            if subdepth > max_sub:
                max_sub = subdepth
                max_child = child
        copy_root = copy.deepcopy(current)
        max_child.father = None
        max_child.addChild()
        max_child.setDepth()
        if max_child.depth >= current_Depth:
            current = copy_root
            break
        else:
            current = max_child
            current_Depth = max_child.depth
    return current


class Prim:
    def __init__(self, mother):
        self.mother = mother

    def perform_Algo(self, component):
        # print("t")
        # print(component)
        # source = component[random.randint(0, len(component) - 1)]
        source = component[0]
        V = component
        U = [source]
        V.remove(source)
        lst_result = []
        while len(V) != 0:
            tup = self.find_min(U, V)
            U.append(tup[1])
            V.remove(tup[1])
            lst_result.append(tup)
        graph = self.lst_to_graph(lst_result, U)
        return graph

    def lst_to_graph(self, lst, component):
        graph = Graph.DenseGraph()
        for vertex in component:
            graph.addVertex(vertex)
        for edges in lst:
            graph.addEdge(str(edges[0]), str(edges[1]), int(edges[2]), False)
        return graph

    def find_min(self, cover, uncover):
        min_weight = 99999
        min_tuple = None
        for co in cover:
            for un in uncover:
                try:
                    weight = self.mother.edges[co][un]
                    if weight < min_weight:
                        min_weight = weight
                        min_tuple = (co, un, int(min_weight))
                    else:
                        continue
                except:
                    continue
        return min_tuple


if __name__ == "__main__":
    # g = Graph.DenseGraph('Subway-Seoul-ver-2.csv')
    g = Graph.DenseGraph('Subway-Seoul-Eng.csv')
    clustering = NewmanClustering()
    components = clustering.performNewmanClustering(g, 3)
    prim = Prim(g)
    graphs = []
    for component in components:
        graphs.append(prim.perform_Algo(component))
    i = 1
    for graph in graphs:
        root = Node(random.choice(graph.vertexes), None, graph)
        root.addChild()
        root.setDepth()
        root = balance(root)
        com = str(i) + ". " + "Component of " + str(graph.vertexes)
        print(com)
        print("Local Supply Tree")
        print(root.getString(0))
        result = "Max. Depth = " + str(float(root.depth))
        print(result)
        print()
        i += 1
