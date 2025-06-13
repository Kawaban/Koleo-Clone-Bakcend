import heapq
from datetime import datetime

from django.db import connections
from geopy.distance import geodesic

from modules.connections.models import Connection

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Result:
    def __init__(self, cost: float,duration:float, train_number: str, departure_time: str, arrival_time: str,
                 start_stop: str, end_stop: str):
        self.cost = cost
        self.duration = duration
        self.train_number = train_number
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.start_stop = start_stop
        self.end_stop = end_stop


class Edge:
    def __init__(self, id: int, line: str,
                 departure_time: str, arrival_time: str,
                 start_stop: str = None, end_stop: str = None, price: float = 0.0):
        self.id = id
        self.line = line
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.start_stop = start_stop
        self.end_stop = end_stop
        self.price = price

    def get_optimization_cost(self,optimization_key, current_time, current_line):
        time_format = "%H:%M:%S"
        t1 = datetime.strptime(current_time, time_format)
        t2 = datetime.strptime(self.arrival_time, time_format)
        t3 = datetime.strptime(self.departure_time, time_format)
        if t1 > t3:
            return float('inf')
        if optimization_key == 't':
            diff_seconds = (t2 - t1).total_seconds()
            diff_float = diff_seconds / 60
            return diff_float


class Node:
    def __init__(self, stop: str, lat: float, lon: float):
        self.stop = stop
        self.lat = lat
        self.lon = lon


class Graph(metaclass=SingletonMeta):
    def __init__(self):
        self.edges = {}
        self.nodes = {}
        self.edges_lines = {}
        self.lines_nodes = {}
        self.adjacency_list = {}
        scheduled_connections = Connection.objects.all()
        for connection in scheduled_connections:
            start_stop = connection.departure_station.name
            end_stop = connection.arrival_station.name
            edge = Edge(
                id=connection.id,
                line=connection.train_number,
                departure_time=connection.departure_time.strftime("%H:%M:%S"),
                arrival_time=connection.arrival_time.strftime("%H:%M:%S"),
                start_stop=start_stop,
                end_stop=end_stop,
                price=connection.price
            )
            self.edges[edge.id] = edge

            if start_stop not in self.nodes:
                self.nodes[start_stop] = Node(
                    stop=start_stop,
                    lat=connection.departure_station.latitude,
                    lon=connection.departure_station.longitude
                )
            if end_stop not in self.nodes:
                self.nodes[end_stop] = Node(
                    stop=end_stop,
                    lat=connection.arrival_station.latitude,
                    lon=connection.arrival_station.longitude
                )

            if start_stop not in self.adjacency_list:
                self.adjacency_list[start_stop] = []
            if end_stop not in self.adjacency_list:
                self.adjacency_list[end_stop] = []

            self.adjacency_list[start_stop].append(edge)



class Algorithm:
    def calculate_path(self,start_stop: str, end_stop: str, optimization_key: str, start_time: str):
        graph = Graph()
        time_format = "%H:%M:%S"
        def get_edge_ids(previous_nodes, edge_ids, start, end):
            path_edges = []
            current = end
            while current is not None and current != start:
                if previous_nodes[current] is not None:
                    path_edges.append(edge_ids[current])
                current = previous_nodes[current]
            path_edges.reverse()
            return path_edges

        def format_output(edges):
            time_format = "%H:%M:%S"
            formatted_edges = []
            current_train = None
            current_start_stop = None
            current_departure_time = None
            prev_end_stop = None
            prev_arrival_time = None
            current_price = 0.0
            for edge_id in edges:
                if current_train is None or graph.edges[edge_id].line == current_train:
                    if current_train is None:
                        current_train = graph.edges[edge_id].line
                        current_start_stop = graph.edges[edge_id].start_stop
                        current_departure_time = graph.edges[edge_id].departure_time
                    prev_end_stop = graph.edges[edge_id].end_stop
                    prev_arrival_time = graph.edges[edge_id].arrival_time
                    current_price += graph.edges[edge_id].price
                else:
                    formatted_edges.append(Result(
                        cost=current_price,
                        duration= (datetime.strptime(prev_arrival_time, time_format) - datetime.strptime(current_departure_time, time_format)).total_seconds(),
                        train_number=current_train,
                        departure_time=current_departure_time,
                        arrival_time=prev_arrival_time,
                        start_stop=current_start_stop,
                        end_stop=prev_end_stop
                    ))

                    current_train = graph.edges[edge_id].line
                    current_start_stop = graph.edges[edge_id].start_stop
                    current_departure_time = graph.edges[edge_id].departure_time
                    prev_end_stop = graph.edges[edge_id].end_stop
                    prev_arrival_time = graph.edges[edge_id].arrival_time
                    current_price = graph.edges[edge_id].price
            return formatted_edges

        def heuristic(node):
            return geodesic((node.lat, node.lon), (graph.nodes[end_stop].lat, graph.nodes[end_stop].lon)).km * 3

        priority_queue = [(0, 0, start_stop, start_time, (None, None))]
        shortest_paths = {node: float('inf') for node in graph.nodes.keys()}
        shortest_paths[start_stop] = 0
        previous_nodes = {node: None for node in graph.nodes}
        edge_ids = {node: None for node in graph.nodes}

        while priority_queue:
            c_d, current_distance, current_node, current_time, current_line = heapq.heappop(priority_queue)

            if current_distance > shortest_paths[current_node]:
                continue

            if current_node == end_stop:
                return format_output(get_edge_ids(previous_nodes, edge_ids, start_stop, end_stop))

            if current_node not in graph.adjacency_list:
                continue

            for neighbor in graph.adjacency_list[current_node]:
                distance = shortest_paths[current_node] + graph.edges[neighbor].get_optimization_cost(optimization_key,
                                                                                                      current_time,
                                                                                                      current_line)
                if distance < shortest_paths[graph.edges[neighbor].end_stop]:
                    shortest_paths[graph.edges[neighbor].end_stop] = distance
                    f_score = distance + heuristic(graph.nodes[graph.edges[neighbor].end_stop])
                    previous_nodes[graph.edges[neighbor].end_stop] = current_node
                    edge_ids[graph.edges[neighbor].end_stop] = graph.edges[neighbor].id
                    heapq.heappush(priority_queue,
                                   (f_score, distance, graph.edges[neighbor].end_stop,
                                    graph.edges[neighbor].arrival_time,
                                    (graph.edges[neighbor].company, graph.edges[neighbor].line)))

        return []

