import sys


class Zone:

    def __init__(self, name: str,
                 x: int,
                 y: int,
                 type_zone: str,
                 color: str,
                 max_drones: int = 1):
        self.name = name
        self.x = x
        self.y = y
        self.type_zone = type_zone
        self.color = color
        self.max_drones = max_drones
    
    def __repr__(self):
        return self.name

    def get_cost(self) -> int:
        if self.type_zone == 'restricted':
            return 2
        return 1


class Connection:
    def __init__(self, zone_1: Zone, zone_2: Zone, max_link: int = 1):
        self.zone_1 = zone_1
        self.zone_2 = zone_2
        self.max_link = max_link


class Graph:

    def __init__(self, number_of_drones: int):
        self.number_of_drones = number_of_drones
        self.zones = []
        self.connections = []
        self.start: Zone | None = None
        self.end: Zone | None = None

    def get_zone_name(self, name: str) -> Zone | None:
        if self.start and self.start.name == name:
            return self.start
        if self.end and self.end.name == name:
            return self.end
        for zone in self.zones:
            if zone.name == name:
                return zone
        return None

    def get_neighbours(self, zone: Zone) -> list[tuple[Zone, Connection]]:
        neighbours = []
        for connect in self.connections:
            if connect.zone_1 == zone:
                neighbours.append(connect.zone_2)
            if connect.zone_2 == zone:
                neighbours.append(connect.zone_1)
        return neighbours


class Parser:

    def parse_coordinate(self, coord: str, name: str) -> int:
        try:
            value = int(coord)
            if value < 0:
                raise Exception(f'{name} has to be positive')
            return value

        except ValueError:
            print(f'{name}) has to be an int')
            sys.exit(1)

        except Exception as e:
            print(e)
            sys.exit(1)

    def parse_zone(self, parts: list[str], graph: Graph) -> Zone:
        valid_zones = ['normal', 'blocked', 'restricted', 'priority']

        name = parts[1]
        if ' ' in name or '-' in name:
            print(f'Invalid zone name: {name}')
            sys.exit(1)

        if graph.get_zone_name(name) is not None:
            print(f'Duplicate zone name: {name}')
            sys.exit(1)

        x = self.parse_coordinate(parts[2], 'X')
        y = self.parse_coordinate(parts[3], 'Y')
        color = None
        zone = 'normal'
        max_drones = 1
        for part in parts[4:]:
            if 'color' in part:
                color = part.split('=')[1].strip('[]\n')
            if 'zone' in part:
                zone = part.split('=')[1].strip('[]\n')
                if zone not in valid_zones:
                    print(f'Invalid zone type: {zone}')
                    sys.exit(1)
            if 'max_drones' in part:
                try:
                    max_drones = int(part.split('=')[1].strip('[]\n'))
                    if max_drones <= 0:
                        raise Exception('max_drones has to be positive')
                except ValueError:
                    print('max_drones has to an int')
                    sys.exit(1)
                except Exception as e:
                    print(e)
                    sys.exit(1)
        return Zone(name, x, y, zone, color, max_drones)

    def parse_connection(self, parts: list[str], graph: Graph) -> Connection:
        names = parts[1].split('-')
        zone_1 = graph.get_zone_name(names[0])
        zone_2 = graph.get_zone_name(names[1])
        value = 1

        if zone_1 is None:
            print(f"Zone '{names[0]}' not found")
            sys.exit(1)

        if zone_2 is None:
            print(f"Zone '{names[1]}' not found")
            sys.exit(1)

        if zone_1 == zone_2:
            print('A zone cannot connect to itself')
            sys.exit(1)

        for existing in graph.connections:
            if (existing.zone_1 == zone_1 and existing.zone_2 == zone_2) or (existing.zone_2 == zone_1 and existing.zone_1 == zone_2):
                print('Duplicate Connection')
                sys.exit(1)

        for meta in parts[2:]:
            if 'max_link_capacity' in meta:
                try:
                    value = int(meta.split('=')[1].strip('[]\n'))
                    if value <= 0:
                        raise Exception('max_link_capacity has to be positive')

                except ValueError:
                    print('max_link_capacity has to be an int')
                    sys.exit(1)

                except Exception as e:
                    print(e)
                    sys.exit(1)

        return Connection(zone_1, zone_2, value)

    def parse(self, filepath: str) -> Graph:

        try:
            with open(filepath) as file:
                lines = file.readlines()
                first_line = None
                first_line_index = 0

                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#'):
                        first_line = stripped
                        first_line_index = i
                        break
                if first_line is None or not first_line.startswith('nb_drones:'):
                    print('First non-empty line must be nb_drones')
                    sys.exit(1)

                graph: Graph | None = None
                parts = first_line.split(':')

                try:
                    number_of_drones = int(parts[1])
                    if number_of_drones <= 0:
                        raise Exception('Number of drones has to be pos')
                    graph = Graph(number_of_drones)

                except ValueError:
                    print('Number of drones has to be an int')

                except Exception as e:
                    print(e)
                    sys.exit(1)

                valid_prefix = ('start_hub:', 'end_hub:', 'hub:', 'connection:', '#')
                for rest_of_lines in lines[first_line_index + 1:]:

                    stripped = rest_of_lines.strip()
                    if stripped == "":
                        continue
                    if not stripped.startswith(valid_prefix):
                        print(f'Invalid line: {stripped}')
                        sys.exit(1)
                    if rest_of_lines.startswith(('start_hub:', 'end_hub:', 'hub:')):
                        parts = rest_of_lines.strip().split()
                        zone = self.parse_zone(parts, graph)
                        if rest_of_lines.startswith('start_hub:'):
                            if graph.start is None:
                                graph.start = zone
                            else:
                                print('start_hub already existed')
                                sys.exit(1)
                        elif rest_of_lines.startswith('end_hub:'):
                            if graph.end is None:
                                graph.end = zone
                            else:
                                print('end_hub already existed')
                                sys.exit(1)
                        elif rest_of_lines.startswith('hub:'):
                            graph.zones.append(zone)

                    if rest_of_lines.startswith('connection:'):
                        parts = rest_of_lines.strip().split()
                        connect = self.parse_connection(parts, graph)
                        graph.connections.append(connect)

            if graph.start is None:
                print('start_hub cannot be None')
                sys.exit(1)
            if graph.end is None:
                print('end_hub cannot be None')
                sys.exit(1)
            if graph is None:
                sys.exit(1)
            return graph

        except FileNotFoundError:
            print(f"Error: file '{sys.argv[1]}' not found")
            sys.exit(1)
        except Exception as e:
            print(e)


