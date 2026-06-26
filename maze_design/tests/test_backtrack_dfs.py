# 回溯/DFS 迷宫生成器 —— 单元测试

import sys
import os
import unittest

# 从 tests/ 的上级目录 src/ 导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from maze import Maze, WALL, PATH, START, END, COIN, TRAP, BOSS
from generators.backtrack_dfs import generate_maze_backtrack_dfs


# 可走格子的集合（非墙即能走，含资源格）
WALKABLE = {PATH, START, END, COIN, TRAP, BOSS}


def _get_all_walkable(grid):
    """返回所有非墙格子的坐标列表"""
    cells = []
    n = len(grid)
    for i in range(n):
        for j in range(n):
            if grid[i][j] in WALKABLE:
                cells.append((i, j))
    return cells


def _bfs_reachable(grid, start):
    """BFS 从 start 出发，返回所有可达的 walkable 坐标集合"""
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
    """统计可走格子之间的连通边数（双向算一次）"""
    walkable = set(_get_all_walkable(grid))
    edges = 0
    n = len(grid)
    for x, y in walkable:
        for dx, dy in [(0, 1), (1, 0)]:  # 只检查右、下，避免重复
            nx, ny = x + dx, y + dy
            if (nx, ny) in walkable:
                edges += 1
    return edges


class TestBacktrackDFS(unittest.TestCase):

    # ── 1. 奇数尺寸基础验证 ────────────────────────────
    def test_odd_size_basic(self):
        n = 15
        maze = Maze(n)
        generate_maze_backtrack_dfs(maze)

        self.assertEqual(maze.n, 15)
        self.assertEqual(len(maze.maze), 15)
        self.assertEqual(len(maze.maze[0]), 15)
        self.assertIsNotNone(maze.start)
        self.assertIsNotNone(maze.end)

    # ── 2. 偶数尺寸基础验证 ────────────────────────────
    def test_even_size_basic(self):
        n = 16
        maze = Maze(n)
        generate_maze_backtrack_dfs(maze)

        self.assertEqual(maze.n, 16)
        self.assertEqual(len(maze.maze), 16)
        self.assertEqual(len(maze.maze[0]), 16)

    # ── 3. 起点终点在边缘 ──────────────────────────────
    def test_start_end_positions(self):
        """起点在边缘，终点在边缘"""
        for n in [15, 16, 5, 8]:
            maze = Maze(n)
            generate_maze_backtrack_dfs(maze)
            sx, sy = maze.start
            ex, ey = maze.end

            self.assertTrue(sx == 0 or sy == 0 or sx == n - 1 or sy == n - 1,
                            f"n={n}: 起点 {maze.start} 不在边缘")
            self.assertTrue(ex == 0 or ey == 0 or ex == n - 1 or ey == n - 1,
                            f"n={n}: 终点 {maze.end} 不在边缘")
            self.assertNotEqual(maze.start, maze.end,
                                "起点和终点不能相同")

    # ── 4. 迷宫连通性测试 ───────────────────────────────
    def test_all_cells_reachable(self):
        """从起点出发，所有 walkable 格子必须可达"""
        for n in [15, 16, 7, 10]:
            maze = Maze(n)
            generate_maze_backtrack_dfs(maze)
            grid = maze.maze

            all_walkable = _get_all_walkable(grid)
            reachable = _bfs_reachable(grid, maze.start)

            for cell in all_walkable:
                self.assertIn(cell, reachable,
                              f"n={n}: 格子 {cell} 不可达，迷宫不连通")

    # ── 5. 完美迷宫（无环）测试 ─────────────────────────
    def test_no_cycles(self):
        """边数 = 节点数 - 1 → 无环 |
        边数 > 节点数 - 1 → 有环"""
        for n in [15, 16, 7, 10, 5, 12]:
            maze = Maze(n)
            generate_maze_backtrack_dfs(maze)
            grid = maze.maze

            walkable_count = len(_get_all_walkable(grid))
            edge_count = _count_edges(grid)

            self.assertEqual(
                edge_count, walkable_count - 1,
                f"n={n}: 边数={edge_count}, walkable={walkable_count}, "
                f"应有 {walkable_count - 1} 条边，实际有 {edge_count} → 存在环路"
            )

    # ── 6. 偶数尺寸空间利用率 ───────────────────────────
    def test_even_no_wasted_space(self):
        """偶数 n 时，第 n-2 行和列不能全是墙"""
        for n in [6, 8, 10, 12, 14, 16]:
            maze = Maze(n)
            generate_maze_backtrack_dfs(maze)
            grid = maze.maze

            # 检查第 n-2 行(14)和第 n-2 列(14)是否有通路
            row_has_path = any(grid[n - 2][j] in WALKABLE for j in range(n))
            col_has_path = any(grid[i][n - 2] in WALKABLE for i in range(n))

            self.assertTrue(row_has_path,
                            f"n={n}: 第 {n-2} 行全为墙，空间浪费")
            self.assertTrue(col_has_path,
                            f"n={n}: 第 {n-2} 列全为墙，空间浪费")

    # ── 7. 外墙完整性（除了起点终点外，全是墙）━━━━━━━━
    def test_outer_walls(self):
        """row0, col0, row(n-1), col(n-1) 除 SE 外全墙"""
        for n in [15, 16, 7, 10]:
            maze = Maze(n)
            generate_maze_backtrack_dfs(maze)
            grid = maze.maze
            sx, sy = maze.start
            ex, ey = maze.end

            for i in range(n):
                if (i, 0) not in {(sx, sy), (ex, ey)}:
                    self.assertEqual(grid[i][0], WALL,
                                     f"n={n}: ({i},0) 不是外墙")
                if (i, n - 1) not in {(sx, sy), (ex, ey)}:
                    self.assertEqual(grid[i][n - 1], WALL,
                                     f"n={n}: ({i},{n-1}) 不是外墙")
            for j in range(n):
                if (0, j) not in {(sx, sy), (ex, ey)}:
                    self.assertEqual(grid[0][j], WALL,
                                     f"n={n}: (0,{j}) 不是外墙")
                if (n - 1, j) not in {(sx, sy), (ex, ey)}:
                    self.assertEqual(grid[n - 1][j], WALL,
                                     f"n={n}: ({n-1},{j}) 不是外墙")

    # ── 8. 多次生成稳定性 ───────────────────────────────
    def test_multiple_generations(self):
        """连续生成 10 次不崩溃、全部通过连通性 + 无环测试"""
        for _ in range(10):
            for n in [15, 16]:
                maze = Maze(n)
                generate_maze_backtrack_dfs(maze)
                grid = maze.maze

                walkable = _get_all_walkable(grid)
                reachable = _bfs_reachable(grid, maze.start)
                self.assertEqual(set(walkable), reachable)
                self.assertEqual(_count_edges(grid), len(walkable) - 1)

    # ── 9. 资源放置验证 ─────────────────────────────────
    def test_resources_placed(self):
        """验证金币、陷阱、BOSS 已被放置"""
        for n in [15, 16]:
            maze = Maze(n)
            generate_maze_backtrack_dfs(maze)
            grid = maze.maze

            coins = sum(1 for row in grid for c in row if c == COIN)
            traps = sum(1 for row in grid for c in row if c == TRAP)
            bosses = sum(1 for row in grid for c in row if c == BOSS)

            self.assertGreater(coins, 0, f"n={n}: 未放置金币")
            self.assertGreater(traps, 0, f"n={n}: 未放置陷阱")
            self.assertGreater(bosses, 0, f"n={n}: 未放置 BOSS")

            # 资源格不应该是墙
            for i in range(n):
                for j in range(n):
                    if grid[i][j] == COIN:
                        self.assertNotEqual((i, j), maze.start,
                                            f"n={n}: 金币不能放在起点")
                        self.assertNotEqual((i, j), maze.end,
                                            f"n={n}: 金币不能放在终点")


if __name__ == '__main__':
    unittest.main(verbosity=2)
