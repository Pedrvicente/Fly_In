import heapq
from parser import Graph, Zone


class Pathfinder:

    def find_path(self, graph: Graph) -> list[Zone]:
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
                    score = priority_cost - (1 if n.type_zone == 'priority' else 0)
                    new_cost = cost + n.get_cost()
                    heapq.heappush(fila, (new_cost, score, id(n), n))
                    previous[n] = current_zone
        return []


if __name__ == '__main__':
    import sys
    from parser import Parser

    parser = Parser()
    graph = parser.parse(sys.argv[1])

    pathfinder = Pathfinder()
    path = pathfinder.find_path(graph)
    for zone in path:
        print(zone.name)
