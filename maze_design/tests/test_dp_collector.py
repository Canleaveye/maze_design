# 动态规划资源收集 —— 单元测试

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from maze import Maze, WALL, PATH, START, END, COIN, TRAP, BOSS
from dp_collector import collect_resources


def _empty_maze(n):
    """创建全墙迷宫"""
    m = Maze(n)
    for i in range(n):
        for j in range(n):
            m.set_cell(i, j, WALL)
    return m


def _connect(maze, x1, y1, x2, y2):
    """打通相邻两格，不覆盖已有的资源格"""
    for x, y in [(x1, y1), (x2, y2)]:
        if maze.get_cell(x, y) == WALL:
            maze.set_cell(x, y, PATH)


class TestDPCollector(unittest.TestCase):

    # ── 1. 直线通路，2 个金币 ─────────────────────────
    def test_straight_coins(self):
        """S - C - C - E  一路收金币"""
        m = _empty_maze(5)
        # 通路行: row 1
        m.set_cell(1, 1, PATH)
        m.set_cell(1, 2, COIN)
        m.set_cell(1, 3, COIN)
        m.set_cell(1, 4, PATH)
        _connect(m, 1, 1, 1, 2)
        _connect(m, 1, 2, 1, 3)
        _connect(m, 1, 3, 1, 4)
        m.set_start(1, 1)
        m.set_end(1, 4)
        value, path = collect_resources(m)
        self.assertEqual(value, 100)

    # ── 2. 主干有陷阱 ────────────────────────────────
    def test_trap_on_spine(self):
        """S - T - E  陷阱在必经之路上"""
        m = _empty_maze(5)
        m.set_cell(1, 1, PATH)
        m.set_cell(1, 2, TRAP)
        m.set_cell(1, 3, PATH)
        _connect(m, 1, 1, 1, 2)
        _connect(m, 1, 2, 1, 3)
        m.set_start(1, 1)
        m.set_end(1, 3)
        value, _ = collect_resources(m)
        self.assertEqual(value, -30)

    # ── 3. 分支有金币，应绕路 ─────────────────────────
    def test_coin_branch(self):
        """  C     coin on branch
            |
            S - E  main path"""
        m = _empty_maze(5)
        _connect(m, 1, 1, 1, 2)   # S - P
        _connect(m, 1, 2, 1, 3)   # P - E
        _connect(m, 0, 2, 1, 2)   # branch up to C
        m.set_cell(0, 2, COIN)
        m.set_start(1, 1)
        m.set_end(1, 3)
        value, _ = collect_resources(m)
        self.assertEqual(value, 50)

    # ── 4. 分支只有陷阱，应跳过 ───────────────────────
    def test_trap_branch_skip(self):
        """  T     trap on branch (skip)
            |
            S - E"""
        m = _empty_maze(5)
        _connect(m, 1, 1, 1, 2)
        _connect(m, 1, 2, 1, 3)
        _connect(m, 0, 2, 1, 2)
        m.set_cell(0, 2, TRAP)
        m.set_start(1, 1)
        m.set_end(1, 3)
        value, _ = collect_resources(m)
        self.assertEqual(value, 0)

    # ── 5. 分支金币+陷阱净赚 ─────────────────────────
    def test_branch_net_positive(self):
        """  C(50)
            |
            T(-30)   net +20
            |
            S - E"""
        m = _empty_maze(7)
        _connect(m, 3, 1, 3, 2)   # S - P
        _connect(m, 3, 2, 3, 3)   # P - E
        _connect(m, 2, 2, 3, 2)   # P up to T
        _connect(m, 1, 2, 2, 2)   # T up to C
        m.set_cell(2, 2, TRAP)
        m.set_cell(1, 2, COIN)
        m.set_start(3, 1)
        m.set_end(3, 3)
        value, _ = collect_resources(m)
        self.assertEqual(value, 20)   # 50 - 30

    # ── 6. 分支净负值，跳过 ──────────────────────────
    def test_branch_net_negative(self):
        """  T(-30)
            |
            C(50)
            |
            T(-30)   可进入前两层得 20，跳过 -30 叶子"""
        m = _empty_maze(9)
        _connect(m, 4, 1, 4, 2)
        _connect(m, 4, 2, 4, 3)
        _connect(m, 3, 2, 4, 2)   # P → T1
        _connect(m, 2, 2, 3, 2)   # T1 → C
        _connect(m, 1, 2, 2, 2)   # C → T2
        m.set_cell(3, 2, TRAP)
        m.set_cell(2, 2, COIN)
        m.set_cell(1, 2, TRAP)
        m.set_start(4, 1)
        m.set_end(4, 3)
        value, _ = collect_resources(m)
        self.assertEqual(value, 20)   # -30+50=20, 跳过 T2(-30)

    # ── 7. 生成迷宫路径合法 ──────────────────────────
    def test_generated_maze(self):
        from generators.backtrack_dfs import generate_maze_backtrack_dfs
        for n in [7, 9, 15]:
            maze = Maze(n)
            generate_maze_backtrack_dfs(maze)
            value, path = collect_resources(maze)
            self.assertEqual(path[0], maze.start)
            self.assertEqual(path[-1], maze.end)
            for k in range(len(path) - 1):
                x1, y1 = path[k]
                x2, y2 = path[k + 1]
                self.assertEqual(abs(x1 - x2) + abs(y1 - y2), 1)

    # ── 8. 路径每步可走 ──────────────────────────────
    def test_path_all_walkable(self):
        from generators.backtrack_dfs import generate_maze_backtrack_dfs
        WALKABLE = {PATH, START, END, COIN, TRAP, BOSS}
        for n in [7, 9, 15]:
            maze = Maze(n)
            generate_maze_backtrack_dfs(maze)
            _, path = collect_resources(maze)
            for x, y in path:
                self.assertIn(maze.get_cell(x, y), WALKABLE)


if __name__ == '__main__':
    unittest.main(verbosity=2)
