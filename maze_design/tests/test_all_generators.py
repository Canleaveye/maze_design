# 迷宫生成器通用测试 —— 适配所有 4 种算法

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from maze import Maze, WALL, PATH, START, END, COIN, TRAP, BOSS
from generators.backtrack_dfs import generate_maze_backtrack_dfs
from generators.divide_conquer import generate_maze_divide_conquer
from generators.greedy import generate_maze_greedy
from generators.branch_bound_bfs import generate_maze_branch_bound_bfs

WALKABLE = {PATH, START, END, COIN, TRAP, BOSS}

GENERATORS = {
    "backtrack_dfs": generate_maze_backtrack_dfs,
    "divide_conquer": generate_maze_divide_conquer,
    "kruskal": generate_maze_greedy,
    "branch_bound_bfs": generate_maze_branch_bound_bfs,
}


def _get_all_walkable(grid):
    return [(i, j) for i in range(len(grid))
            for j in range(len(grid[0])) if grid[i][j] in WALKABLE]


def _bfs_reachable(grid, start):
    n = len(grid)
    visited = set()
    queue = [start]
    visited.add(start)
    while queue:
        x, y = queue.pop(0)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < n:
                if (nx, ny) not in visited and grid[nx][ny] in WALKABLE:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    return visited


def _count_edges(grid):
    walkable = set(_get_all_walkable(grid))
    edges = 0
    n = len(grid)
    for x, y in walkable:
        for dx, dy in [(0, 1), (1, 0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in walkable:
                edges += 1
    return edges


class TestAllGenerators(unittest.TestCase):

    sizes = [15, 16]

    def test_all_connected(self):
        for name, func in GENERATORS.items():
            for n in self.sizes:
                m = Maze(n)
                func(m)
                grid = m.maze
                walkable = _get_all_walkable(grid)
                reachable = _bfs_reachable(grid, m.start)
                for cell in walkable:
                    self.assertIn(cell, reachable,
                                  f"{name} n={n}: {cell} unreachable")

    def test_all_no_cycles(self):
        for name, func in GENERATORS.items():
            for n in self.sizes:
                m = Maze(n)
                func(m)
                wc = len(_get_all_walkable(m.maze))
                ec = _count_edges(m.maze)
                self.assertEqual(ec, wc - 1,
                                 f"{name} n={n}: edges={ec} walkable={wc} -> cycle!")

    def test_all_outer_walls(self):
        for name, func in GENERATORS.items():
            for n in self.sizes:
                m = Maze(n)
                func(m)
                grid = m.maze
                size = len(grid)
                sx, sy = getattr(m, 'start', (-1, -1))
                ex, ey = getattr(m, 'end', (-1, -1))
                for i in range(size):
                    if (i, 0) not in {(sx, sy), (ex, ey)}:
                        self.assertEqual(grid[i][0], WALL)
                    if (i, size - 1) not in {(sx, sy), (ex, ey)}:
                        self.assertEqual(grid[i][size - 1], WALL)
                for j in range(size):
                    if (0, j) not in {(sx, sy), (ex, ey)}:
                        self.assertEqual(grid[0][j], WALL)
                    if (size - 1, j) not in {(sx, sy), (ex, ey)}:
                        self.assertEqual(grid[size - 1][j], WALL)

    def test_all_resources_placed(self):
        for name, func in GENERATORS.items():
            for n in self.sizes:
                m = Maze(n)
                func(m)
                grid = m.maze
                coins = sum(1 for r in grid for c in r if c == COIN)
                traps = sum(1 for r in grid for c in r if c == TRAP)
                bosses = sum(1 for r in grid for c in r if c == BOSS)
                self.assertGreater(coins, 0, f"{name} n={n}: no coins")
                self.assertGreater(traps, 0, f"{name} n={n}: no traps")
                self.assertGreater(bosses, 0, f"{name} n={n}: no boss")

    def test_all_multiple_runs(self):
        for name, func in GENERATORS.items():
            for _ in range(3):
                m = Maze(15)
                func(m)
                wc = len(_get_all_walkable(m.maze))
                self.assertEqual(_count_edges(m.maze), wc - 1)

    def test_all_even_no_waste(self):
        for name, func in GENERATORS.items():
            n = 16
            m = Maze(n)
            func(m)
            grid = m.maze
            row_ok = any(grid[n-2][j] in WALKABLE for j in range(n))
            col_ok = any(grid[i][n-2] in WALKABLE for i in range(n))
            self.assertTrue(row_ok, f"{name} n={n}: row {n-2} all walls")
            self.assertTrue(col_ok, f"{name} n={n}: col {n-2} all walls")


if __name__ == '__main__':
    unittest.main(verbosity=2)
