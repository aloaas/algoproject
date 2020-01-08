import random
import numpy as np

# Used ideas for code from https://scipython.com/blog/making-a-maze (Christian Hill, April 2017)

class Cell:
    """
    A cell in maze is a point in the grid which may be surrounded by walls in all four directions
    (north, east, south or west).
    """

    # A wall separates a pair of cells in the N-S or W-E directions.
    wall_pairs = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

    def __init__(self, x, y):
        """In the beginning cell is surrounded by walls."""
        self.x, self.y = x, y
        self.walls = {'N': True, 'S': True, 'E': True, 'W': True}

    def has_all_walls(self):
        """Check if cell all 4 walls"""
        return all(self.walls.values())

    def knock_down_wall(self, other, wall):
        """Knock down the wall between cells self and other."""

        self.walls[wall] = False
        other.walls[Cell.wall_pairs[wall]] = False


class Maze:

    def __init__(self, nx, ny, ix=0, iy=0, f=1):
        """
        The maze consists of nx * ny cells and will be constructed starting
        from the home cell with location (ix, iy). The number of food places is defined by f.
        """
        self.f = f
        self.nx, self.ny = nx, ny
        self.ix, self.iy = ix, iy
        self.maze_map = np.zeros([self.nx, self.ny], dtype=object)

        # filling maze map
        for y in range(ny):
            for x in range(nx):
                self.maze_map[x, y] = Cell(x, y)

    def cell_at(self, x, y):
        """Cell at location (x,y)"""
        return self.maze_map[x][y]

    def to_numpy(self):
        """
        Convert the map of cells to numpy array after the maze map is ready.
        """
        maze_rows = np.full([1, nx * 2 + 1], 1)  # maze is surrounded by 1 (wall)

        for y in range(ny):

            maze_row = np.array([[1]])  # row starts with 1 (wall)
            for x in range(nx):
                if self.maze_map[x][y].walls['E']:
                    maze_row = np.append(maze_row, 0)
                    maze_row = np.append(maze_row, 1)
                else:
                    maze_row = np.append(maze_row, 0)
                    maze_row = np.append(maze_row, 0)
            maze_rows = np.append(maze_rows, np.array([maze_row]), axis=0)

            maze_row = np.array([[1]])  # row starts with 1 (wall)
            for x in range(nx):
                if self.maze_map[x][y].walls['S']:
                    maze_row = np.append(maze_row, 1)
                    maze_row = np.append(maze_row, 1)
                else:
                    maze_row = np.append(maze_row, 0)
                    maze_row = np.append(maze_row, 1)
            maze_rows = np.append(maze_rows, np.array([maze_row]), axis=0)

        return maze_rows

    def find_valid_neighbours(self, cell):
        """Find unvisited neighbours of given cell."""

        delta = [('W', (-1, 0)),
                 ('E', (1, 0)),
                 ('S', (0, 1)),
                 ('N', (0, -1))]
        neighbours = []
        for direction, (dx, dy) in delta:
            x2, y2 = cell.x + dx, cell.y + dy
            if (0 <= x2 < nx) and (0 <= y2 < ny):
                neighbour = maze.cell_at(x2, y2)
                if neighbour.has_all_walls():
                    neighbours.append((direction, neighbour))
        return neighbours

    def place_food(self, final_map):
        """Randomly choose a place where to put food."""

        fx = random.randint(1, nx * 2 - 1)
        occupied = True

        # until we have found an empty spot (denoted by 0)
        while occupied:
            fy = random.randint(1, ny * 2 - 1)
            if final_map[fx][fy] == 0:
                final_map[fx][fy] = 2  # food is denoted by 2
                occupied = False

        return final_map

    def make_maze(self):

        n = self.nx * self.ny
        cell_stack = []
        current_cell = self.cell_at(ix, iy)
        nv = 1  # total number of visited cells during maze construction

        while nv < n:
            neighbours = self.find_valid_neighbours(current_cell)

            if not neighbours: # dead-end
                current_cell = cell_stack.pop()
                continue

            # choose a random neighbouring cell and move to it
            direction, next_cell = random.choice(neighbours)
            current_cell.knock_down_wall(next_cell, direction)
            cell_stack.append(current_cell)
            current_cell = next_cell
            nv += 1

        # when maze is ready, place required number of foods on empty spaces
        i = 0
        np_maze = self.to_numpy()
        np_maze[2 * ix + 1][2 * iy + 1] = 3  # add home location (denoted by 3)

        while i < self.f:
            final_map = self.place_food(np_maze)
            i += 1

        return final_map


nx, ny = 10, 10 # grid size
ix, iy = 1, 1 # home location
f = 5 # number of food places

maze = Maze(nx, ny, ix, iy, f)
final_maze = maze.make_maze()
print(final_maze)