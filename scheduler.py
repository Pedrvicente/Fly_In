from parser import Zone, Graph
from pathfinder import Pathfinder
from rich.console import Console
from rich.table import Table


class Drone:
    def __init__(self, drone_id: int, start: Zone) -> None:
        self.drone_id = drone_id
        self.position = start
        self.path_index = 0

    def __repr__(self) -> str:
        return f'D{self.drone_id}@{self.position.name}'

    def move_drone(self, next_zone: Zone, next_index: int) -> None:
        self.position = next_zone
        self.path_index = next_index


class Scheduler:
    def __init__(self, graph: Graph, path: list[Zone]):
        self.graph = graph
        self.path = path
        self.number_of_drones = self.graph.number_of_drones
        self.all_zones = [self.graph.start] + self.graph.zones + [self.graph.end]
        self.zone_occupancy = {i: 0 for i in self.all_zones}
        self.zone_occupancy[self.graph.start] = self.number_of_drones

        self.drones: list[Drone] = []
        for i in range(1, self.graph.number_of_drones + 1):
            self.drones.append(Drone(i, self.graph.start))

    def run(self) -> list[str]:
        turns = 0
        output = []
        while self.zone_occupancy[self.graph.end] < self.number_of_drones:
            print(f'Turno {turns}: occupancy={self.zone_occupancy}')
            sorted_drones = sorted(self.drones, key=lambda d: d.path_index, reverse=True)
            turns += 1
            turn_moves = []
            for drone in sorted_drones:
                if drone.position == self.graph.end:
                    continue
                next_index = drone.path_index + 1
                next_zone = self.path[next_index]
                current_zone = drone.position
                if next_zone == self.graph.end:
                    can_move = True
                else:
                    can_move = self.zone_occupancy[next_zone] < next_zone.max_drones
                if can_move:
                    self.zone_occupancy[next_zone] += 1
                    self.zone_occupancy[current_zone] -= 1
                    drone.move_drone(next_zone, next_index)
                    turn_moves.append(f"D{drone.drone_id}-{next_zone.name}")
            output.append(' '.join(turn_moves))
        return output


if __name__ == '__main__':
    import sys
    from parser import Parser

    parser = Parser()
    graph = parser.parse(sys.argv[1])

    pathfinder = Pathfinder()
    path = pathfinder.find_path(graph)
    if not path:
        print('No path found between start and end')
        sys.exit(1)
    
    console = Console()
    console.print("[green]zona normal[/green]")
    console.print("[red]zona blocked[/red]")
    console.print("[yellow]zona restricted[/yellow]")
    console.print("[blue]zona priority[/blue]")

    sch = Scheduler(graph, path)
    print(sch.run())
    
    