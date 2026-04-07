from parser import Zone, Graph


class Drone:
    """Represents a single drone navigating the routing network.

    Attributes:
        drone_id: Unique integer identifier for this drone.
        position: Current zone the drone occupies.
        path_index: Index of the drone's current position in the assigned path.
    """

    def __init__(self, drone_id: int, start: Zone) -> None:
        """Initialize a Drone at the starting zone.

        Args:
            drone_id: Unique identifier for this drone.
            start: The starting zone where the drone begins.
        """
        self.drone_id = drone_id
        self.position = start
        self.path_index = 0

    def __repr__(self) -> str:
        """Return string representation of the drone.

        Returns:
            String in the format 'D<id>@<zone_name>'.
        """
        return f'D{self.drone_id}@{self.position.name}'

    def move_drone(self, next_zone: Zone, next_index: int) -> None:
        """Move the drone to a new zone and update its path index.

        Args:
            next_zone: The zone to move the drone to.
            next_index: The new path index after the move.
        """
        self.position = next_zone
        self.path_index = next_index


class Scheduler:
    """Schedules drone movements along a path through the network.

    Manages turn-by-turn simulation of all drones, enforcing zone
    occupancy rules and recording movement history.

    Attributes:
        graph: The routing graph.
        path: Ordered list of zones from start to end.
        number_of_drones: Total number of drones being routed.
        all_zones: All zones in the graph including start and end.
        zone_occupancy: Current drone count per zone.
        drones: List of all Drone instances.
    """

    def __init__(self, graph: Graph, path: list[Zone]) -> None:
        """Initialize the Scheduler with a graph and a planned path.

        Args:
            graph: The routing graph containing zones and connections.
            path: Ordered list of zones representing the route to follow.
        """
        self.graph = graph
        self.path = path
        self.number_of_drones = self.graph.number_of_drones
        start_list = [self.graph.start]
        end_list = [self.graph.end]
        self.all_zones = start_list + self.graph.zones + end_list
        self.zone_occupancy: dict = {i: 0 for i in self.all_zones}
        self.zone_occupancy[self.graph.start] = self.number_of_drones

        self.drones: list[Drone] = []
        for i in range(1, self.graph.number_of_drones + 1):
            self.drones.append(Drone(i, self.graph.start))

    def run(self) -> tuple[list[str], list[dict], list[list[dict]]]:
        """Run the simulation until all drones reach the end zone.

        On each turn, drones are processed in order of advancement along
        the path. A drone moves if the next zone has available capacity.

        Returns:
            A tuple of:
                - output: List of turn strings in 'D<id>-<zone>' format.
                - history: List of zone occupancy snapshots per turn.
                - movements: List of per-turn movement detail records.
        """
        turns = 0
        output = []
        history = []
        movements = []
        while self.zone_occupancy[self.graph.end] < self.number_of_drones:
            sorted_drones = sorted(
                self.drones,
                key=lambda d: d.path_index,
                reverse=True
            )
            turns += 1
            turn_moves = []
            turn_movements: list[dict] = []
            for drone in sorted_drones:
                if drone.position == self.graph.end:
                    continue
                next_index = drone.path_index + 1
                next_zone = self.path[next_index]
                current_zone = drone.position
                if next_zone == self.graph.end:
                    can_move = True
                else:
                    occupancy = self.zone_occupancy[next_zone]
                    can_move = occupancy < next_zone.max_drones
                if can_move:
                    self.zone_occupancy[next_zone] += 1
                    self.zone_occupancy[current_zone] -= 1
                    drone.move_drone(next_zone, next_index)
                    turn_moves.append(f"D{drone.drone_id}-{next_zone.name}")
                    turn_movements.append({
                        'drone_id': drone.drone_id,
                        'from': current_zone,
                        'to': next_zone
                    })
            movements.append(turn_movements)
            history.append(self.zone_occupancy.copy())
            output.append(' '.join(turn_moves))
        return output, history, movementss
