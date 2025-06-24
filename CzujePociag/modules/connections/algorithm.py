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
        print("calculate_path called with:", start_stop, end_stop, optimization_key, start_time)        
        graph = Graph()
        print("Graph nodes:", list(graph.nodes.keys()))
        print("Graph adjacency_list:", {k: [e.end_stop for e in v] for k, v in graph.adjacency_list.items()})
        
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
            print("Formatting output for edges:", edges)
            time_format = "%H:%M:%S"
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
                    # Add the completed segment to formatted_edges
                    formatted_edges.append(Result(
                        cost=current_price,
                        duration=(datetime.strptime(prev_arrival_time, time_format) - datetime.strptime(current_departure_time, time_format)).total_seconds(),
                        train_number=current_train,
                        departure_time=current_departure_time,
                        arrival_time=prev_arrival_time,
                        start_stop=current_start_stop,
                        end_stop=prev_end_stop
                    ))
                    # Start new segment
                    current_train = edge.line
                    current_start_stop = edge.start_stop
                    current_departure_time = edge.departure_time
                    prev_end_stop = edge.end_stop
                    prev_arrival_time = edge.arrival_time
                    current_price = edge.price
            
            # Add the last segment
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

        def heuristic(node):
            return geodesic((graph.nodes[node].lat, graph.nodes[node].lon), 
                          (graph.nodes[end_stop].lat, graph.nodes[end_stop].lon)).km * 3

        # Initialize data structures
        priority_queue = [(0, 0, start_stop, start_time, (None, None))]
        shortest_paths = {node: float('inf') for node in graph.nodes.keys()}
        shortest_paths[start_stop] = 0
        previous_nodes = {node: None for node in graph.nodes.keys()}
        edge_ids = {node: None for node in graph.nodes.keys()}

        print("Initial priority_queue:", priority_queue)
        
        while priority_queue:
            current_cost, current_distance, current_node, current_time, (current_line, _) = heapq.heappop(priority_queue)
            print("Processing node:", current_node, "Distance:", current_distance)

            if current_distance > shortest_paths[current_node]:
                continue

            if current_node == end_stop:
                path_edges = get_edge_ids(previous_nodes, edge_ids, start_stop, end_stop)
                print("Path found! Edges:", path_edges)
                if not path_edges:  # No path found
                    return []
                return format_output(path_edges)

            if current_node not in graph.adjacency_list:
                continue

            for edge in graph.adjacency_list[current_node]:
                neighbor = edge.end_stop
                optimization_cost = edge.get_optimization_cost(optimization_key, current_time, current_line)
                
                if optimization_cost == float('inf'):
                    continue
                    
                distance = shortest_paths[current_node] + optimization_cost

                if distance < shortest_paths[neighbor]:
                    shortest_paths[neighbor] = distance
                    f_score = distance + heuristic(neighbor)
                    previous_nodes[neighbor] = current_node
                    edge_ids[neighbor] = edge.id
                    heapq.heappush(priority_queue, (f_score, distance, neighbor, edge.arrival_time, (edge.line, edge.id)))

        # No path found
        return []

