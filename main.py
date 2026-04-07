import sys
from parser import Parser
from pathfinder import Pathfinder
from scheduler import Scheduler
from visualizer import Visualizer


def main() -> None:
    if len(sys.argv) < 2:
        print('To few arguments')
        sys.exit(1)
    parser = Parser()
    graph = parser.parse(sys.argv[1])
    visual = '--visual' in sys.argv

    pathfinder = Pathfinder()
    path = pathfinder.find_path(graph)
    if not path:
        print('No path found between start and end')
        sys.exit(1)

    sch = Scheduler(graph, path)
    output, history, movements = sch.run()
    for line in output:
        print(line)

    if visual:
        ani = Visualizer(graph)
        ani.animate(history, movements)


if __name__ == '__main__':
    main()
