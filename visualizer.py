from typing import Any

from parser import Graph, Zone
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class Visualizer:
    """Provides graphical animation of the drone routing simulation.

    Renders the zone graph and animates drone movements frame by frame
    using matplotlib.

    Attributes:
        graph: The routing graph to visualize.
        connections: List of connections between zones.
        all_zones: All zones including start and end.
        fig: Matplotlib figure for rendering.
        ax: Matplotlib axes for drawing.
    """

    def __init__(self, graph: Graph) -> None:
        """Initialize the Visualizer with a routing graph.

        Args:
            graph: The routing graph containing zones and connections.
        """
        self.graph = graph
        self.connections = graph.connections
        assert graph.start is not None
        assert graph.end is not None
        self.all_zones = [graph.start] + graph.zones + [graph.end]
        plt.ion()
        self.fig, self.ax = plt.subplots()

    def draw_graph(self, state: dict[Zone, int]) -> None:
        """Draw the zone graph with current occupancy labels.

        Args:
            state: Mapping of each zone to its current drone count.
        """
        for zone in self.all_zones:
            try:
                self.ax.scatter(zone.x, zone.y, c=zone.color, s=300)
            except ValueError:
                self.ax.scatter(zone.x, zone.y, c='gray', s=300)

            self.ax.annotate(
                f"{zone.type_zone}\n"
                f"capacity: {state[zone]}/{zone.max_drones}",
                (zone.x + 0.20, zone.y), fontsize=8)
        for connection in self.connections:
            self.ax.plot(
                [connection.zone_1.x, connection.zone_2.x],
                [connection.zone_1.y, connection.zone_2.y],
            )

    def animate(
        self,
        history: list[dict[Zone, int]],
        movements: list[list[dict[str, Any]]]
    ) -> None:
        """Animate the simulation by interpolating drone positions per turn.

        Each simulation turn is split into sub-frames to show smooth drone
        movement between zones.

        Args:
            history: List of zone occupancy snapshots, one per turn.
            movements: List of per-turn movement records, each containing
                'from', 'to', and 'drone_id' keys.
        """
        self.history = history
        self.movements = movements
        all_frames = []
        for n, m in zip(self.history, self.movements):
            for progress in [0, 0.25, 0.5, 0.75, 1.0]:
                all_frames.append((n, m, progress))

        def update(
            frame: tuple[dict[Zone, int], list[dict[str, Any]], float],
        ) -> list[Any]:
            """Update the animation for a single frame.

            Args:
                frame: Tuple of (state, moves, progress) where progress
                    is a float in [0, 1] representing interpolation factor.
            """
            n, m, progress = frame
            self.ax.clear()
            self.draw_graph(n)
            for move in m:
                x = move['from'].x + progress * (
                    move['to'].x - move['from'].x
                )
                y = move['from'].y + progress * (
                    move['to'].y - move['from'].y
                )
                self.ax.scatter(x, y, c='black', s=200)
            return []

        self.ani = FuncAnimation(
            self.fig, update, frames=all_frames, interval=300
        )
        plt.ioff()
        plt.show()
