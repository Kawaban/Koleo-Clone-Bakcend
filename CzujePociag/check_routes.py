import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from modules.connections.algorithm import Algorithm

# Test the route finding
algorithm = Algorithm()
routes = algorithm.calculate_path(
    start_stop="Wrocław Główny",
    end_stop="Poznań Główny",
    optimization_key='t',
    start_time="00:00:00",
    n_paths=5  # default value
)

print("\nAvailable routes from Wrocław Główny to Poznań Główny:")
print("-" * 70)

for i, path in enumerate(routes, 1):
    print(f"\nRoute {i}:")
    total_cost = 0
    total_duration = 0
    
    for segment in path:
        print(f"Train: {segment.train_number}")
        print(f"From: {segment.departure_station} at {segment.departure_time}")
        print(f"To: {segment.arrival_station} at {segment.arrival_time}")
        print(f"Price: {segment.cost} PLN")
        print(f"Duration: {segment.duration/60:.0f} minutes")
        print("-" * 30)
        total_cost += float(segment.cost)
        total_duration += segment.duration
    
    print(f"Total Cost: {total_cost:.2f} PLN")
    print(f"Total Duration: {total_duration/60:.0f} minutes")
    print("-" * 70) 