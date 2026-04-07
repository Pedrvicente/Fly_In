import heapq
from parser import Graph, Zone


class Pathfinder:
    """Finds optimal paths through the drone routing graph using A*.

    Uses a priority queue (min-heap) to explore zones in order of movement
    cost, preferring priority zones and avoiding blocked zones.
    """

    def find_path(self, graph: Graph) -> list[Zone]:
        """Find the lowest-cost path from start to end in the graph.

        Uses a modified Dijkstra/A* approach that accounts for zone movement
        costs and prefers priority zones via a secondary score.

        Args:
            graph: The routing graph containing zones and connections.

        Returns:
            Ordered list of zones from start to end, or empty list if no
            path exists.
        """
        start = graph.start
        end = graph.end
        fila = [(0, 0, id(start), start)]
        visited = {start}
        previous = {}

        while fila:
            cost, priority_cost, _, current_zone = heapq.heappop(fila)

            if current_zone == end:
                path = []
                current = end
                while current != start:
                    path.append(current)
                    current = previous[current]
                path.append(start)
                path.reverse()
                return path

            neighbours = graph.get_neighbours(current_zone)
            for n in neighbours:
                if n not in visited:
                    if n.type_zone == 'blocked':
                        continue
                    visited.add(n)
                    score = priority_cost - (
                        1 if n.type_zone == 'priority' else 0
                    )
                    new_cost = cost + n.get_cost()
                    heapq.heappush(fila, (new_cost, score, id(n), n))
                    previous[n] = current_zone
        return []
