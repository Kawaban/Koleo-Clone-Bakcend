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
    def __init__(self, cost: float, duration: float, train_number: str, departure_time: str, arrival_time: str,
                 start_stop: str, end_stop: str):
        self.cost = cost
        self.duration = duration
        self.train_number = train_number
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.departure_station = start_stop  # Map start_stop to departure_station
        self.arrival_station = end_stop      # Map end_stop to arrival_station


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
        self.price = Decimal(str(price))

    def __str__(self):
        return self.line

    def get_optimization_cost(self,optimization_key, current_time, current_line):
        time_format = "%H:%M:%S"
        # Ensure we're working with string times
        if isinstance(current_time, datetime):
            current_time = current_time.strftime(time_format)
            
        t1 = datetime.strptime(current_time, time_format)
        t2 = datetime.strptime(self.arrival_time, time_format)
        t3 = datetime.strptime(self.departure_time, time_format)
        
        if t1 > t3:
            return float('inf')
            
        if optimization_key == 't':
            diff_seconds = (t2 - t1).total_seconds()
            diff_float = diff_seconds / 60
            return diff_float
        
        return float('inf')  # Default case if optimization key not recognized


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
            current_price = Decimal('0.00')
            
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

            if current_train is not None:
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

        def is_valid_path(path_edges):
            if not path_edges:
                return False
            
            current_time = start_time
            for edge_id in path_edges:
                edge = graph.edges[edge_id]
                if datetime.strptime(edge.departure_time, time_format) < datetime.strptime(current_time, time_format):
                    return False
                current_time = edge.arrival_time
            return True

        # Initialize data structures
        paths_found = []
        visited = set()
        
        def find_paths(current_stop, current_path, current_time, visited_stops):
            if len(paths_found) >= n_paths:
                return
                
            if current_stop == end_stop:
                if is_valid_path(current_path):
                    formatted_path = format_output(current_path)
                    if formatted_path:
                        paths_found.append(formatted_path)
                return
            
            # Get all possible next edges
            for edge_id in graph.adjacency_list.get(current_stop, []):
                edge = graph.edges[edge_id]
                next_stop = edge.end_stop
                
                # Skip if we've visited this stop or if timing doesn't work
                if (next_stop in visited_stops or 
                    datetime.strptime(edge.departure_time, time_format) < datetime.strptime(current_time, time_format)):
                    continue
                
                # Try this path
                visited_stops.add(next_stop)
                find_paths(next_stop, current_path + [edge_id], edge.arrival_time, visited_stops)
                visited_stops.remove(next_stop)
        
        # Start the recursive search
        visited.add(start_stop)
        find_paths(start_stop, [], start_time, visited)
        
        return paths_found or []  # Return empty list if no paths found
