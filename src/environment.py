from mazelib import Maze
from mazelib.generate.Prims import Prims
from random import Random
import numpy as np


class Environment:
    """
    Creates a new Maze instance

    Parameters
    -----------
    width: The width to set the inner maze to
    height: The height to set the inner maze to
    seed: (optional) The provided initial seed

    (see `Environment.random_seed(random)`)

    """

    UP = 0
    DOWN = 1
    RIGHT = 2
    LEFT = 3

    SCALE = 2

    def random_seed(random: Random):
        """
        Creates a randomized seed usable as the base seed of mazes

        Parameters
        -----------
        random: The Random instance to generate a random seed from

        Returns
        --------
        The randomized seed usable for the Environment
        """
        return random.randint(0, 2**23 - 1)

    def __init__(
        self, height: int = 10, width: int = 10, seed=None, render_layout=True
    ):
        self.maze = Maze(seed)
        self.maze.generator = Prims(height, width)
        self.maze.generate()

        self.show_layout = render_layout

        self.width, self.height = self.maze.grid.shape

        self.maze.generate_entrances(start_outer=False, end_outer=True)

        self.y, self.x = self.maze.start
        self.goal_y, self.goal_x = self.maze.end

        self.maze.grid[self.goal_y][self.goal_x] = 0

    def get_observations(self):
        """Returns the observations of the current state as a numpy array"""
        if self.show_layout:
            obs = self.maze.grid.flatten().copy()
            size = int(obs.size)
            obs.resize(size + 2 * (self.width + self.height) + 4, refcheck=False)
        else:
            obs = np.zeros(2 * (self.width + self.height) + 4)
            size = 0
        obs[size + self.x] = 1
        obs[size + self.width + self.y] = 1
        obs[size + self.width + self.height + self.goal_x] = 1
        obs[size + 2 * self.width + self.height + self.goal_y] = 1
        obs[size + 2 * self.width + 2 * self.height + 0] = 1 if self.can_move(Environment.UP) else 0
        obs[size + 2 * self.width + 2 * self.height + 1] = 1 if self.can_move(Environment.DOWN) else 0
        obs[size + 2 * self.width + 2 * self.height + 2] = 1 if self.can_move(Environment.LEFT) else 0
        obs[size + 2 * self.width + 2 * self.height + 3] = 1 if self.can_move(Environment.RIGHT) else 0
        return obs

    def get_obs_length(self):
        """Returns the length of observations returned from this array"""
        return int(self.get_observations().size)

    def set_position(self, x, y) -> bool:
        """
        Attempts to set the current position.

        Checks that the following are true
        - (x,y) is not out of bounds of the maze
        - (x,y) is not a wall in the maze

        If both conditions are met, the current position is changed

        Returns `True` if successful. Returns `False` otherwise
        """
        if self.is_valid_position(x, y):
            self.x, self.y = x, y
            return True
        return False

    def get_valid_positions(self):
        return [
            (i % self.width, i // self.width)
            for i in range(self.width * self.height)
            if self.maze.grid[i // self.width][i % self.width] == 0
        ]

    def is_valid_position(self, x, y):
        return (y == self.goal_y and x == self.goal_x) or (
            y >= 0
            and y < self.height
            and x >= 0
            and x < self.width
            and self.maze.grid[y][x] == 0
        )

    def move(self, move: int):
        if move == self.UP:
            return self.set_position(self.x, self.y - 1)
        if move == self.DOWN:
            return self.set_position(self.x, self.y + 1)
        if move == self.RIGHT:
            return self.set_position(self.x + 1, self.y)
        if move == self.LEFT:
            return self.set_position(self.x - 1, self.y)

    def can_move(self, move: int):
        if move == self.UP:
            return self.is_valid_position(self.x, self.y - 1)
        if move == self.DOWN:
            return self.is_valid_position(self.x, self.y + 1)
        if move == self.RIGHT:
            return self.is_valid_position(self.x + 1, self.y)
        if move == self.LEFT:
            return self.is_valid_position(self.x - 1, self.y)

    def is_solved(self):
        return self.x == self.goal_x and self.y == self.goal_y

    def get_reward(self) -> float:
        if self.is_solved():
            return 10.0
        else:
            return -0.1
        # dist = abs(self.x - self.goal_x) + abs(self.y - self.goal_y)
        # max_dist = self.width + self.height
        # scale = Environment.SCALE
        # return ((max_dist - dist) ** scale) / (max_dist**scale)
