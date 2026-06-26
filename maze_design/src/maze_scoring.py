# 迷宫评分模块 —— 区分度 / 稳定性 / 平衡性 三维评价
# 使用多个难度不同的 AI 在迷宫上跑分，计算三指标 + 总分

import sys
import os
import random
import math
from collections import deque

sys.path.insert(0, os.path.dirname(__file__))

from maze import Maze, WALL, PATH, START, END, COIN, TRAP, BOSS, DIRECTIONS, COIN_VALUE, TRAP_VALUE
from dp_collector import collect_resources
from greedy_player import GreedyPlayer

WALKABLE_SET = {PATH, START, END, COIN, TRAP, BOSS}


class RandomWalker:
    """纯随机漫游 AI —— 底线基准"""
    def __init__(self, maze):
        self.maze = maze
        self.grid = maze.maze
        self.n = maze.n
        self.pos = maze.start
        self.end = maze.end
        self.collected = 0
        self.steps = 0
        self.path = [self.pos]
        self.collected_at = set()
        self.traps_hit = set()

    def step(self):
        x, y = self.pos
        # 随机选一个 walkable 邻居
        neighbors = []
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.n and 0 <= ny < self.n:
                if self.grid[nx][ny] in WALKABLE_SET:
                    neighbors.append((nx, ny))
        if not neighbors:
            return False

        nxt = random.choice(neighbors)
        self.pos = nxt
        self.steps += 1
        self.path.append(self.pos)

        val = self.grid[nxt[0]][nxt[1]]
        if val == COIN and nxt not in self.collected_at:
            self.collected += COIN_VALUE
            self.collected_at.add(nxt)
        elif val == TRAP and nxt not in self.traps_hit:
            self.collected += TRAP_VALUE
            self.traps_hit.add(nxt)
        return self.pos != self.end

    def play(self, max_steps=50000):
        while self.pos != self.end and self.steps < max_steps:
            if not self.step():
                break
        return self.collected


def _spearman_rank(arr):
    """返回 arr 中每个元素的 Spearman 秩（最大值排第 1）"""
    n = len(arr)
    indexed = sorted(enumerate(arr), key=lambda t: t[1], reverse=True)
    ranks = [0] * n
    for rank, (idx, _) in enumerate(indexed):
        ranks[idx] = rank + 1
    return ranks


def _spearman_correlation(a, b):
    """Spearman 相关系数"""
    n = len(a)
    if n < 2:
        return 0.0
    ra = _spearman_rank(a)
    rb = _spearman_rank(b)
    d2 = sum((ra[i] - rb[i]) ** 2 for i in range(n))
    return 1.0 - (6.0 * d2) / (n * (n * n - 1))


def _percentile_rank(values, target):
    """target 在 values 中的百分位排名 [0, 1]"""
    if not values:
        return 0.5
    below = sum(1 for v in values if v < target)
    equal = sum(1 for v in values if v == target)
    return (below + 0.5 * equal) / len(values)


def evaluate_mazes(maze_list, ai_runners, expected_ranks, eps=1e-9):
    """
    评价一组迷宫的质量

    参数:
        maze_list:       [maze_1, maze_2, ...]
        ai_runners:      [run_ai_1(maze)->score, run_ai_2(maze)->score, ...]
                         ai_1 应为最强 AI, ai_m 最弱
        expected_ranks:  期望的 AI 排名 [1, 2, 3, ...] (1=最强)
        eps:             防零小常数

    返回:
        list of {mazeIndex, scores_per_ai, D, C, B, total}
    """
    m = len(ai_runners)   # AI 数量
    p = len(maze_list)    # 迷宫数量

    # 1. 跑分：score_matrix[ai][maze]
    score_matrix = []
    for ai_idx, runner in enumerate(ai_runners):
        row = []
        for maze in maze_list:
            row.append(runner(maze))
        score_matrix.append(row)

    # 2. 每个迷宫的标准差
    stds = []
    means = []
    ai_ranks_per_maze = []  # 每个迷宫给出的 AI 排名
    for j in range(p):
        col = [score_matrix[i][j] for i in range(m)]
        stds.append(_std(col))
        means.append(sum(col) / m)
        # 迷宫 j 给出的 AI 排名（分值最高的 AI 排第 1）
        ai_ranks_per_maze.append(_spearman_rank(col))

    max_std = max(stds) if max(stds) > 0 else 1.0

    results = []
    for j in range(p):
        # 区分度 D
        D = stds[j] / (max_std + eps)

        # 稳定性 C: Spearman(迷宫j的AI排名, 期望AI排名)
        spearman = _spearman_correlation(ai_ranks_per_maze[j], expected_ranks)
        C = (spearman + 1) / 2.0

        # 平衡性 B
        q = _percentile_rank(means, means[j])
        B = 4 * q * (1 - q)

        total = 100 * (D * C * B) ** (1.0 / 3.0)

        results.append({
            "mazeIndex": j,
            "scores": [score_matrix[i][j] for i in range(m)],
            "mean": round(means[j], 2),
            "std": round(stds[j], 2),
            "aiRanks": ai_ranks_per_maze[j],
            "D_discrimination": round(D, 4),
            "C_stability": round(C, 4),
            "B_balance": round(B, 4),
            "totalScore": round(total, 2),
        })

    return results


def _std(values):
    if len(values) < 2:
        return 0.0
    m = sum(values) / len(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))
