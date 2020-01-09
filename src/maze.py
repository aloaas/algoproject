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
        self.maze_rows = np.full([1, self.nx * 2 + 1], 1)  # final maze map as numpy array
        self.food_locations = []  # coordinates of the placed food places

        # filling maze map with cells
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
        # self.maze_rows = np.full([1, self.nx * 2 + 1], 1)  # maze is surrounded by 1 (wall)

        for y in range(self.ny):

            maze_row = np.array([[1]])  # row starts with 1 (wall)
            for x in range(self.nx):
                if self.maze_map[x][y].walls['E']:
                    maze_row = np.append(maze_row, 0)
                    maze_row = np.append(maze_row, 1)
                else:
                    maze_row = np.append(maze_row, 0)
                    maze_row = np.append(maze_row, 0)
            self.maze_rows = np.append(self.maze_rows, np.array([maze_row]), axis=0)

            maze_row = np.array([[1]])  # row starts with 1 (wall)
            for x in range(self.nx):
                if self.maze_map[x][y].walls['S']:
                    maze_row = np.append(maze_row, 1)
                    maze_row = np.append(maze_row, 1)
                else:
                    maze_row = np.append(maze_row, 0)
                    maze_row = np.append(maze_row, 1)
            self.maze_rows = np.append(self.maze_rows, np.array([maze_row]), axis=0)

        return self.maze_rows

    def find_valid_neighbours(self, cell):
        """Find unvisited neighbours of given cell."""

        delta = [('W', (-1, 0)),
                 ('E', (1, 0)),
                 ('S', (0, 1)),
                 ('N', (0, -1))]
        neighbours = []
        for direction, (dx, dy) in delta:
            x2, y2 = cell.x + dx, cell.y + dy
            if (0 <= x2 < self.nx) and (0 <= y2 < self.ny):
                neighbour = self.cell_at(x2, y2)
                if neighbour.has_all_walls():
                    neighbours.append((direction, neighbour))
        return neighbours

    def place_food(self):
        """Randomly choose a place where to put food."""
        occupied = True

        # until we have found an empty spot (denoted by 0)
        while occupied:
            fx = random.randint(1, self.nx * 2 - 2)  # -2 becuase we dont want to remove the outer wall
            fy = random.randint(1, self.ny * 2 - 2)
            if self.maze_rows[fy][fx] == 0:
                self.maze_rows[fy][fx] = 2  # food is denoted by 2
                self.food_locations.append((fy, fx))  # store locations where food was placed
                occupied = False

        # return self.maze_rows

    def remove_random_walls(self):
        """Randomly remove some of existing walls in order for the final maze to have more different
        possibilities for the ants to move. Number of removed walls is 25% of total surface."""
        cur_remove = 0  # number of walls that have been removed so far
        remove = 0.25 * self.nx * self.ny  # number of walls to remove - 25% of total surface

        # remove the right number of walls
        while cur_remove < remove:

            wall = False

            # find a wall (denoted by 1)
            while not wall:
                fx = random.randint(1, self.nx * 2 - 1)  # -2 because we dont want to remove the outer wall
                fy = random.randint(1, self.ny * 2 - 1)
                if self.maze_rows[fy][fx] == 1:
                    self.maze_rows[fy][fx] = 0  # wall -> empty space
                    wall = True
            cur_remove += 1

        return self.maze_rows

    def remove_walls_around_point(self, x, y):
        '''Remove all the walls surroundig point (x,y). This helps to avoid food blocking the maze.'''

        self.maze_rows[x + 1][y] = 0
        self.maze_rows[x][y + 1] = 0
        self.maze_rows[x - 1][y] = 0
        self.maze_rows[x][y - 1] = 0
        self.maze_rows[x + 1][y + 1] = 0
        self.maze_rows[x + 1][y - 1] = 0
        self.maze_rows[x - 1][y + 1] = 0
        self.maze_rows[x - 1][y - 1] = 0

    def repair_outer_wall(self):
        '''If food/home was placed next to outer wall, then 'remove_walls_around_point' removed it.
        Therefore we need to fix the outer wall.'''

        for i in range(self.nx * 2):
            self.maze_rows[0][i] = 1
            self.maze_rows[0][i] = 1

        for j in range(self.ny * 2):
            self.maze_rows[j][0] = 1
            self.maze_rows[j][self.ny * 2] = 1

    def make_maze(self):

        n = self.nx * self.ny
        cell_stack = []
        current_cell = self.cell_at(self.ix, self.iy)
        nv = 1  # total number of visited cells during maze construction

        while nv < n:
            neighbours = self.find_valid_neighbours(current_cell)

            if not neighbours:  # dead-end
                current_cell = cell_stack.pop()
                continue

            # choose a random neighbouring cell and move to it
            direction, next_cell = random.choice(neighbours)
            current_cell.knock_down_wall(next_cell, direction)
            cell_stack.append(current_cell)
            current_cell = next_cell
            nv += 1

        self.to_numpy()  # changes from cells based maze to numpy based maze
        self.remove_random_walls()  # make the maze more sparse

        self.maze_rows[2 * self.ix + 1][2 * self.iy + 1] = 3  # add home location (denoted by 3)
        self.remove_walls_around_point(2 * self.ix + 1, 2 * self.iy + 1)  # remove walls around home

        # place required number of foods on empty spaces
        i = 0
        while i < self.f:
            self.place_food()
            i += 1

        # remove walls around food locations
        for x, y in self.food_locations:
            self.remove_walls_around_point(x, y)

        self.repair_outer_wall()

        return self.maze_rows

