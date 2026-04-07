from parser import Graph, Zone
from scheduler import Scheduler
from pathfinder import Pathfinder
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class Visualizer:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.connections = graph.connections
        self.all_zones = [graph.start] + graph.zones + [graph.end]
        plt.ion()
        self.fig, self.ax = plt.subplots()

    def draw_graph(self, state: dict):
        for zone in self.all_zones:
            self.ax.scatter(zone.x, zone.y, c=zone.color, s=300)
            self.ax.annotate(
                f"zone name: {zone.name}\n"
                f"capacity: {state[zone]}/{zone.max_drones}",
                (zone.x + 0.15, zone.y), fontsize=8)
        for connection in self.connections:
            self.ax.plot(
                [connection.zone_1.x, connection.zone_2.x],
                [connection.zone_1.y, connection.zone_2.y],
                )

    def animate(self, history: list[dict], movements: list[dict]) -> None:
        self.history = history
        self.movements = movements
        all_frames = []
        for n, m in zip(self.history, self.movements):
            for progress in [0, 0.25, 0.5, 0.75, 1.0]:
                all_frames.append((n, m, progress))
        
        def update(frame):
            n, m, progress = frame
            self.ax.clear()
            self.draw_graph(n)
            for move in m:
                x = move['from'].x + progress * (move['to'].x - move['from'].x)
                y = move['from'].y + progress * (move['to'].y - move['from'].y)
                self.ax.scatter(x, y, c='black', s=200)
            
        self.ani = FuncAnimation(self.fig, update, frames=all_frames, interval=300)
        plt.ioff()
        plt.show()




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

    sch = Scheduler(graph, path)
    mom = Visualizer(graph)
    output, history, movements = sch.run()
    mom.animate(history, movements)
    # import matplotlib.pyplot as plt

    # fig, ax = plt.subplots()
    # ax.scatter([0, 3, 10], [0, 4, 10], s=300)
    # ax.annotate('hub', (0, 0))
    # ax.annotate('roof1', (3, 4))
    # ax.annotate('goal', (10, 10))
    # plt.show()
