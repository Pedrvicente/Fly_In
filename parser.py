import sys


class Zone:
    """Represents a zone (node) in the drone routing network.

    Attributes:
        name: Unique identifier for the zone.
        x: X-coordinate of the zone.
        y: Y-coordinate of the zone.
        type_zone: Zone type (normal, blocked, restricted, priority).
        color: Optional display color for visual representation.
        max_drones: Maximum drones allowed in this zone simultaneously.
    """

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        type_zone: str,
        color: str | None,
        max_drones: int = 1
    ) -> None:
        """Initialize a Zone instance.

        Args:
            name: Unique identifier for the zone.
            x: X-coordinate of the zone.
            y: Y-coordinate of the zone.
            type_zone: Zone type (normal, blocked, restricted, priority).
            color: Optional display color string.
            max_drones: Maximum simultaneous occupancy. Defaults to 1.
        """
        self.name = name
        self.x = x
        self.y = y
        self.type_zone = type_zone
        self.color = color
        self.max_drones = max_drones

    def __repr__(self) -> str:
        """Return string representation of the zone.

        Returns:
            The zone name.
        """
        return self.name

    def get_cost(self) -> int:
        """Return the movement cost in turns to enter this zone.

        Returns:
            2 for restricted zones, 1 for all other zone types.
        """
        if self.type_zone == 'restricted':
            return 2
        return 1


class Connection:
    """Represents a connection between two zones.

    Attributes:
        zone_1: First zone.
        zone_2: Second zone.
        max_link: Maximum drones circulating this connection simultaneously.
    """

    def __init__(
        self, zone_1: Zone, zone_2: Zone, max_link: int = 1
    ) -> None:
        """Initialize a Connection instance.

        Args:
            zone_1: First zone endpoint.
            zone_2: Second zone endpoint.
            max_link: Maximum simultaneous capacity. Defaults to 1.
        """
        self.zone_1 = zone_1
        self.zone_2 = zone_2
        self.max_link = max_link


class Graph:
    """Represents the drone routing network as a graph.

    Attributes:
        number_of_drones: Total number of drones to route.
        zones: List of regular hub zones.
        connections: List of connections between zones.
        start: Starting zone for all drones.
        end: Destination zone for all drones.
    """

    def __init__(self, number_of_drones: int) -> None:
        """Initialize an empty Graph.

        Args:
            number_of_drones: Number of drones to simulate.
        """
        self.number_of_drones = number_of_drones
        self.zones: list[Zone] = []
        self.connections: list[Connection] = []
        self.start: Zone | None = None
        self.end: Zone | None = None

    def get_zone_name(self, name: str) -> Zone | None:
        """Find a zone by name across all zones including start and end.

        Args:
            name: The zone name to search for.

        Returns:
            The matching Zone, or None if not found.
        """
        if self.start and self.start.name == name:
            return self.start
        if self.end and self.end.name == name:
            return self.end
        for zone in self.zones:
            if zone.name == name:
                return zone
        return None

    def get_neighbours(self, zone: Zone) -> list[Zone]:
        """Return all zones directly connected to the given zone.

        Args:
            zone: The zone to find neighbours for.

        Returns:
            List of zones adjacent to the given zone via connections.
        """
        neighbours: list[Zone] = []
        for connect in self.connections:
            if connect.zone_1 == zone:
                neighbours.append(connect.zone_2)
            if connect.zone_2 == zone:
                neighbours.append(connect.zone_1)
        return neighbours


class Parser:
    """Parses drone routing map files into a Graph object."""

    def parse_coordinate(self, coord: str, name: str) -> int:
        """Parse a coordinate string into an integer.

        Args:
            coord: String representation of the coordinate.
            name: Axis name used in error messages (e.g. 'X' or 'Y').

        Returns:
            Integer coordinate value.
        """
        try:
            value = int(coord)
            return value
        except ValueError:
            print(f'{name}) has to be an int')
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

    def parse_zone(self, parts: list[str], graph: Graph) -> Zone:
        """Parse a hub definition line into a Zone object.

        Args:
            parts: The result of .strip().split() of a line of the map.
            graph: The graph being built, used to check for duplicate names.

        Returns:
            A new Zone parsed from the input parts.
        """
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
        color: str | None = None
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
                    max_drones = int(
                        part.split('=')[1].strip('[]\n')
                    )
                    if max_drones <= 0:
                        raise ValueError(
                            'max_drones has to be positive'
                        )
                except ValueError as e:
                    print(e)
                    sys.exit(1)
        return Zone(name, x, y, zone, color, max_drones)

    def parse_connection(
        self, parts: list[str], graph: Graph
    ) -> Connection:
        """Parse a connection definition line into a Connection object.

        Args:
            parts: The result of .strip().split() of a line of the map.
            graph: The graph being built, used to validate zone names.

        Returns:
            A new Connection between the two specified zones.
        """
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
            if (
                existing.zone_1 == zone_1 and existing.zone_2 == zone_2
            ) or (
                existing.zone_2 == zone_1 and existing.zone_1 == zone_2
            ):
                print('Duplicate Connection')
                sys.exit(1)

        for meta in parts[2:]:
            if 'max_link_capacity' in meta:
                try:
                    value = int(meta.split('=')[1].strip('[]\n'))
                    if value <= 0:
                        raise ValueError(
                            'max_link_capacity has to be positive'
                        )
                except ValueError as e:
                    print(e)
                    sys.exit(1)

        return Connection(zone_1, zone_2, value)

    def parse(self, filepath: str) -> Graph:
        """Parse a map file and return the corresponding Graph.

        Args:
            filepath: Path to the map file to parse.

        Returns:
            A fully constructed Graph object.
        """
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
                if (
                    first_line is None
                    or not first_line.startswith('nb_drones:')
                ):
                    print('First non-empty line must be nb_drones')
                    sys.exit(1)

                graph: Graph | None = None
                parts = first_line.split(':')

                try:
                    number_of_drones = int(parts[1])
                    if number_of_drones <= 0:
                        raise ValueError(
                            'Number of drones has to be positive'
                        )
                    graph = Graph(number_of_drones)
                except ValueError as e:
                    print(e)
                    sys.exit(1)

                valid_prefix = (
                    'start_hub:', 'end_hub:', 'hub:', 'connection:', '#'
                )
                for rest_of_lines in lines[first_line_index + 1:]:
                    stripped = rest_of_lines.strip()
                    if stripped == "":
                        continue
                    if not stripped.startswith(valid_prefix):
                        print(f'Invalid line: {stripped}')
                        sys.exit(1)
                    if rest_of_lines.startswith(
                        ('start_hub:', 'end_hub:', 'hub:')
                    ):
                        parts = rest_of_lines.strip().split()
                        zone = self.parse_zone(parts, graph)
                        if rest_of_lines.startswith('start_hub:'):
                            # verificar que start_hub já não existia
                            if graph.start is None:
                                graph.start = zone
                            else:
                                print('start_hub already existed')
                                sys.exit(1)
                        elif rest_of_lines.startswith('end_hub:'):
                            # verificar que end_hub já não existia
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
            sys.exit(1)
