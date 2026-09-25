import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import csv
from navigation.navigation_controller import simulate_vehicle_navigation, save_telemetry_csv

path = []
with open('outputs/planned_path.csv', 'r') as f:
    for row in csv.DictReader(f):
        path.append({'x': float(row['x']), 'y': float(row['y']), 'resolution': float(row['resolution'])})

print('Loaded planned cells:', len(path))
result = simulate_vehicle_navigation(path)
print('Simulation Success:', result['success'])
print(f"Total Time: {result['total_time_sec']} s, Total Distance: {result['total_distance_m']} m, Avg Speed: {result['average_speed_mps']} m/s")
print(f"Telemetry Samples: {result['telemetry_samples']}, Waypoints: {result['num_waypoints']}")
out_csv = save_telemetry_csv(result['history'])
print('Saved telemetry to:', out_csv)
print("\nFirst 3 telemetry steps:")
for sample in result['history'][:3]:
    print('  ', sample)
print("\nFinal 3 telemetry steps:")
for sample in result['history'][-3:]:
    print('  ', sample)
