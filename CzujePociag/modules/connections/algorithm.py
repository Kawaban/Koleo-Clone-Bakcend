import heapq
from datetime import datetime
from decimal import Decimal

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

    def __str__(self):
        return self.line

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

    def __str__(self):
        return self.stop


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

            self.adjacency_list[start_stop].append(edge.id)



class Algorithm:
    def calculate_path(self, start_stop: str, end_stop: str, optimization_key: str, start_time: str = "00:00:00", n_paths: int = 1):
        graph = Graph()
        time_format = "%H:%M:%S"

        def get_edge_ids(prev_nodes, edge_ids, start, end):
            path_edges = []
            current = end
            while current is not None and current != start:
                if prev_nodes[current] is not None:
                    path_edges.append(edge_ids[current])
                current = prev_nodes[current]
            path_edges.reverse()
            return path_edges

        def format_output(edges):
            formatted_edges = []
            current_train = None
            current_start_stop = None
            current_departure_time = None
            prev_end_stop = None
            prev_arrival_time = None
            current_price = Decimal('0.0')
            for edge_id in edges:
                edge = graph.edges[edge_id]
                if current_train is None or edge.line == current_train:
                    if current_train is None:
                        current_train = edge.line
                        current_start_stop = edge.start_stop
                        current_departure_time = edge.departure_time
                    prev_end_stop = edge.end_stop
                    prev_arrival_time = edge.arrival_time
                    current_price += edge.price
                else:
                    formatted_edges.append(Result(
                        cost=current_price,
                        duration=(datetime.strptime(prev_arrival_time, time_format) - datetime.strptime(current_departure_time, time_format)).total_seconds(),
                        train_number=current_train,
                        departure_time=current_departure_time,
                        arrival_time=prev_arrival_time,
                        start_stop=current_start_stop,
                        end_stop=prev_end_stop
                    ))

                    current_train = edge.line
                    current_start_stop = edge.start_stop
                    current_departure_time = edge.departure_time
                    prev_end_stop = edge.end_stop
                    prev_arrival_time = edge.arrival_time
                    current_price = edge.price
            formatted_edges.append(Result(
                cost=current_price,
                duration=(datetime.strptime(prev_arrival_time, time_format) - datetime.strptime(current_departure_time, time_format)).total_seconds(),
                train_number=current_train,
                departure_time=current_departure_time,
                arrival_time=prev_arrival_time,
                start_stop=current_start_stop,
                end_stop=prev_end_stop
            ))
            return formatted_edges

        def heuristic(node):
            return geodesic((node.lat, node.lon), (graph.nodes[end_stop].lat, graph.nodes[end_stop].lon)).km * 3


        open_set = []
        heapq.heappush(open_set, (0, 0, start_stop, start_time, (None, None), [], []))

        found_paths = []

        while open_set and len(found_paths) < n_paths:
            f_score, cost_so_far, current_node, current_time, current_line, path_nodes, path_edge_ids = heapq.heappop(open_set)

            new_path_nodes = path_nodes + [current_node]

            if current_node == end_stop:
                found_paths.append(format_output(path_edge_ids))
                continue

            if current_node not in graph.adjacency_list:
                continue

            for edge_id in graph.adjacency_list[current_node]:
                edge = graph.edges[edge_id]
                neighbor = edge.end_stop

                if neighbor in new_path_nodes:
                    continue

                new_cost = cost_so_far + edge.get_optimization_cost(optimization_key, current_time, current_line)
                est_total = new_cost + heuristic(graph.nodes[neighbor])
                new_path_edges = path_edge_ids + [edge.id]

                heapq.heappush(open_set, (
                    est_total,
                    new_cost,
                    neighbor,
                    edge.arrival_time,
                    edge.line,
                    new_path_nodes,
                    new_path_edges
                ))

        return found_paths
