# 动态规划资源收集路径规划

from collections import deque
from maze import WALL, PATH, START, END, COIN, TRAP, BOSS, DIRECTIONS, COIN_VALUE, TRAP_VALUE

WALKABLE_SET = {PATH, START, END, COIN, TRAP, BOSS}

VALUE_MAP = {COIN: COIN_VALUE, TRAP: TRAP_VALUE, PATH: 0, START: 0, END: 0, BOSS: 0}


def _resource_value(grid, pos):
    return VALUE_MAP.get(grid[pos[0]][pos[1]], 0)


def _get_neighbors(grid, n, pos):
    x, y = pos
    result = []
    for dx, dy in DIRECTIONS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < n and 0 <= ny < n and grid[nx][ny] in WALKABLE_SET:
            result.append((nx, ny))
    return result


def _bfs_path(adj, start, end):
    """BFS 找 start→end 路径"""
    parent = {}
    queue = deque([start])
    parent[start] = None
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if v not in parent:
                parent[v] = u
                queue.append(v)
                if v == end:
                    path = []
                    node = end
                    while node is not None:
                        path.append(node)
                        node = parent[node]
                    return path[::-1]
    return []


def _collect_branch_walk(walk, adj, best, node, parent, on_step=None):
    """递归构造分支行走序列，每步触发回调"""
    walk.append(node)
    if on_step:
        on_step(walk[:], node)
    for child in adj[node]:
        if child == parent:
            continue
        if best.get(child, 0) > 0:
            _collect_branch_walk(walk, adj, best, child, node, on_step)
    if parent is not None:
        walk.append(parent)
        if on_step:
            on_step(walk[:], parent)


def collect_resources(maze, on_step=None):
    """
    动态规划：计算从起点到终点的最优资源收集方案

    参数:
        maze:    Maze 对象
        on_step: 可选回调 on_step(walk_list, current_pos)，每步触发

    返回:
        (max_value, path_walk)
    """
    grid = maze.maze
    n = maze.n
    start = maze.start
    end = maze.end

    adj = {}
    for i in range(n):
        for j in range(n):
            if grid[i][j] in WALKABLE_SET:
                adj[(i, j)] = _get_neighbors(grid, n, (i, j))

    spine = _bfs_path(adj, start, end)
    spine_set = set(spine)

    best = {}

    def compute_subtree(node, parent, seen):
        if node in seen:
            return
        seen.add(node)
        val = _resource_value(grid, node)
        child_total = 0
        for child in adj[node]:
            if child == parent or child in spine_set:
                continue
            compute_subtree(child, node, seen)
            child_total += max(0, best.get(child, 0))
        best[node] = max(0, val + child_total)

    total_value = 0
    walk = [start]
    if on_step:
        on_step(walk[:], start)
    seen_global = set()

    for i, node in enumerate(spine):
        if node != start and node != end:
            total_value += _resource_value(grid, node)

        prev = spine[i - 1] if i > 0 else None
        nxt = spine[i + 1] if i + 1 < len(spine) else None

        for child in adj[node]:
            if child == prev or child == nxt or child in spine_set:
                continue
            compute_subtree(child, node, seen_global)
            if best.get(child, 0) > 0:
                total_value += best[child]
                _collect_branch_walk(walk, adj, best, child, node, on_step)

        if nxt is not None:
            walk.append(nxt)
            if on_step:
                on_step(walk[:], nxt)

    return total_value, walk


def collect_resources_snapshots(maze, sample_rate=1):
    """运行 DP 并采集过程快照，用于动画

    返回: (max_value, path_walk, snapshots)
        snapshots: list of (grid_copy, walk_set, current_pos)
    """
    grid = maze.maze
    snapshots = []

    def on_step(walk_list, current_pos):
        if len(snapshots) % sample_rate == 0:
            grid_copy = [row[:] for row in grid]
            snapshots.append((grid_copy, set(walk_list), current_pos))

    max_value, path_walk = collect_resources(maze, on_step=on_step)
    return max_value, path_walk, snapshots
