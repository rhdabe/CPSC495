from src.Network import *
from src.Node import *
# graph = { 1:{2:2,3:1},
#            2:{1:2,3:8},
#            3:{1:1,2:8,6:4,4:2},
#            4:{3:2,6:4,5:7},
#            5:{6:5,4:7},
#            6:{3:4,4:4,5:5}}


def routingTables(network):
    tables = {}

    graph= network.get_better_graph()

    paths = shortest_paths(graph)
    for node in graph.keys():
        table = {}

        for path in paths:
            if(path.__contains__(node)):
                index = path.index(node)

                for i in range(0, len(path)):
                    if i < index:
                        table[path[i]] = path[index - 1]
                    elif i > index:
                        table[path[i]] = path[index + 1]

            tables[node] = table

    # This contains "routing tables" for switches as well, which we need to remove from the result.
    # Also, will change Dest_node field from a Node reference to an IP address,
    # and replace next_node entries by several entries, one for each network layer interface that node possesses.
    only_router_tables = {}

    for node in tables:
        only_router_tables[node] = {}
        if isinstance(node, Router):
            # for each router in the graph
            for dest_node in tables[node]:
                # for each destination node in this node's routing table
                # look up the next node...
                next_node = tables[node][dest_node]
                # to look up the connection between this node and the next node...
                next_connection = (Network.network.connections[Network.network.get_node_pair_id(node.node_id, next_node.node_id)])
                # and get the interfaces from the connection...
                con_interfaces = next_connection.interfaces
                # so we can determine which interface goes from this node to the next node
                next_interface = con_interfaces[0] if con_interfaces[0].node.node_id == node.node_id else con_interfaces[1]
                for interface in dest_node.interfaces.values():
                    # for every interface on the destination node, add an entry to the forwarding table
                    # which specifies next_interface as the one to send traffic out on.
                    only_router_tables[node][interface.IP_address] = next_interface

    return only_router_tables

def shortest_paths(graph):
    paths = []
    graph_copy = graph.copy()

    for source in graph_copy.keys():
        for dest in graph_copy.keys():
            if source != dest and len(graph_copy)>1:
                paths.append(dijkstra(graph_copy, source, dest))
    return paths

#This is here because Python is dumb.
def dijkstra(graph, source_id, dest_id):
    return dijkstra2(graph, source_id, dest_id,[],{},{})

def dijkstra2(graph, source_node, dest_node, visited=[], distances={}, parents={}):
    #Redone to use object info in graph instead of just numbers.

    unvisited = [graph.keys()]

    if source_node == dest_node:
        # We build the shortest path and display it
        path = []
        distances[dest_node] = []
        parent = dest_node
        while parent != None:
            path.append(parent)
            parent = parents.get(parent, None)  # D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.

        path.reverse()

        return path
    else:
        # if it is the initial  run, initializes the cost and visited dict is empty
        if not visited:
            distances[source_node] = 0
        # visit the neighbors
        for neighbor in graph[source_node]:
            if neighbor not in visited:
                new_distance = distances[source_node] + graph[source_node][neighbor].get_latency()
                # graph[source_id][neighbor] returns list of the nodes connected to source
                if new_distance < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_distance
                    parents[neighbor] = source_node  # source id will become parent
        # mark as visited
        visited.append(source_node)
        # now that all neighbors have been visited: recurse
        # unvisited.pop(source_id)
        # select the non visited node with lowest distance 'x'
        # run Dijskstra with src='x'
        unvisited = {}
        for k in graph:
            if k not in visited:  # if key is not in visited dict
                unvisited[k] = distances.get(k, float('inf'))  # D.get(k[,d]) -> D[k] if k in D,defaults to infinity.
                # get the distances for all unvisited nodes and put it into unvisited dict with distances as values.
        # for getting minimum value out of those
        #  x = min(unvisited, key=unvisited.get)
        node_with_minvalue = min(unvisited, key=lambda k: unvisited.get(k,None))
        return dijkstra2(graph, node_with_minvalue, dest_node, visited, distances, parents)


# def dijkstra2(graph, source_id, dest_id, visited=[], distances={}, parents={}):
#
#     unvisited = [graph.keys()]
#
#     if source_id == dest_id:
#         # We build the shortest path and display it
#         path = []
#         distances[dest_id] = []
#         parent = dest_id
#         while parent != None:
#             path.append(parent)
#             parent = parents.get(parent, None)  # D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
#
#         path.reverse()
#
#         return path
#     else:
#         # if it is the initial  run, initializes the cost and visited dict is empty
#         if not visited:
#             distances[source_id] = 0
#         # visit the neighbors
#         for neighbor in graph[source_id]:
#             if neighbor not in visited:
#                 new_distance = distances[source_id] + graph[source_id][neighbor]
#                 # graph[source_id][neighbor] returns list of the nodes connected to source
#                 if new_distance < distances.get(neighbor, float('inf')):
#                     distances[neighbor] = new_distance
#                     parents[neighbor] = source_id  # source id will become parent
#         # mark as visited
#         visited.append(source_id)
#         # now that all neighbors have been visited: recurse
#         # unvisited.pop(source_id)
#         # select the non visited node with lowest distance 'x'
#         # run Dijskstra with src='x'
#         unvisited = {}
#         for k in graph:
#             if k not in visited:  # if key is not in visited dict
#                 unvisited[k] = distances.get(k, float('inf'))  # D.get(k[,d]) -> D[k] if k in D,defaults to infinity.
#                 # get the distances for all unvisited nodes and put it into unvisited dict with distances as values.
#         # for getting minimum value out of those
#         #  x = min(unvisited, key=unvisited.get)
#         node_with_minvalue = min(unvisited, key=lambda k: unvisited.get(k,None))
#         return dijkstra2(graph, node_with_minvalue, dest_id, visited, distances, parents)



