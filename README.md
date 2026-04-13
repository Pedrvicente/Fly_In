*This project has been created as part of the 42 curriculum by pedde-al.*

# Fly-in — Drone Routing Simulation

## Description

Fly-in is a drone routing simulation system that navigates a fleet of drones from a central base to a target location across a network of connected zones. The goal is to move all drones from the start zone to the end zone in the fewest possible simulation turns, while respecting zone capacity constraints, connection limits, and movement costs.

The system parses a custom map file format, finds an optimal path using a modified Dijkstra algorithm, schedules drone movements turn by turn, and provides both terminal output and an optional graphical animation.

## Instructions

### Requirements

- Python 3.10 or later
- pip or pip3

### Installation

```bash
make install
```

This installs all dependencies listed in `requirements.txt` (flake8, mypy, matplotlib).

### Running the simulation

```bash
make run FILE=path/to/map.txt
```

This outputs the step-by-step drone movements to the terminal in the required format:

```
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal
```

### Running with graphical visualisation

```bash
make visualize FILE=path/to/map.txt
```

This runs the simulation and opens an animated matplotlib window showing the drone movements across the zone graph.

### Other commands

```bash
make debug FILE=path/to/map.txt   # Run with Python debugger (pdb)
make clean                         # Remove __pycache__ and .mypy_cache
make lint                          # Run flake8 and mypy
make lint-strict                   # Run mypy --strict
```

### Map file format

```
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
connection: hub-roof1
connection: hub-corridorA
connection: corridorA-goal [max_link_capacity=2]
```

## Algorithm

### Pathfinding — Modified Dijkstra

The pathfinder uses a priority queue (min-heap via `heapq`) to explore zones in order of accumulated movement cost. Zone types affect cost:

- `normal` — 1 turn (default)
- `priority` — 1 turn, but preferred via a secondary score in the heap tuple `(cost, priority_score, id, zone)`
- `restricted` — 2 turns
- `blocked` — inaccessible, skipped during traversal

Priority zones are preferred by subtracting 1 from a secondary score, so when two paths have equal cost, the one passing through more priority zones wins. Blocked zones are filtered out before being added to the queue.

### Scheduling — Turn-by-turn pipeline

The Scheduler processes all drones each turn in order from most advanced (highest path index) to least advanced. This ensures the drone closest to the goal moves first, freeing up space for drones behind it.

Each turn:
1. Drones are sorted by `path_index` descending.
2. Drones with `hold_drone > 1` are waiting (restricted zone penalty) — they decrement and skip.
3. Each remaining drone checks if the next zone has capacity (`zone_occupancy[next_zone] < next_zone.max_drones`).
4. If capacity is available, the drone moves, zone occupancy is updated, and the move is recorded.
5. When a drone enters a `restricted` zone, `hold_drone` is set to 2, causing it to wait one extra turn before moving again.

The end zone accepts unlimited drones.

**Limitations:** The current implementation routes all drones along a single path. Maps with multiple viable paths would benefit from distributing drones across them.

## Visual Representation

The `Visualizer` class uses `matplotlib` with `FuncAnimation` to animate the simulation. Each simulation turn is split into 5 sub-frames (at progress 0, 0.25, 0.5, 0.75, 1.0), interpolating drone positions along the connection line between zones.

Features:
- Zones are coloured according to their `color` field in the map file, with a gray fallback for unrecognised colour names
- Each zone displays its current occupancy and maximum capacity
- Moving drones are shown as black dots sliding along connection lines
- The graph layout uses the actual `x` and `y` coordinates from the map file

Run with `make visualize FILE=...` or pass `--visual` to `main.py` directly.

## Resources

### References

- BFS and DFS (for understanding Dijkstra's algorithm): https://www.youtube.com/watch?v=pcKY4hjDrxk&pp=ygUVYmZzIGFuZCBkZnMgdHJhdmVyc2Fs
- Dijkstra's algorithm: https://www.youtube.com/watch?v=XB4MIexjvY0&t=876s&pp=ygUPZGlqa3N0cmEgbWV0aG9k
- Heap Sort (for understanding heapq): https://www.youtube.com/watch?v=HqPJF2L5h9U&t=1604s&pp=ygUJaGVhcCBzb3J0
- Matplotlib `FuncAnimation`: [matplotlib.org/FuncAnimation](https://matplotlib.org/stable/api/animation_api.html)

### AI Usage

Claude was used throughout this project as a learning companion, not to generate code directly, but to guide understanding through questions and explanations. Specific uses:

- **Parser:** Discussed the file format structure and validation logic.
- **Pathfinding:** Dijkstra's algorithm was explained conceptually.
- **Scheduler:** The turn-by-turn pipeline logic and the restricted zone handling were debugged collaboratively.
- **Visualiser:** matplotlib `FuncAnimation` was introduced and explained.
- **Makefile and project structure:** Rules and best practices.