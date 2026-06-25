# 辅助工具函数模块

import maze as MAZE
from collections import deque
import random as _random


# ── 连通性校验 ────────────────────────────────────────

def is_connected(maze):
    queue = deque()
    visited = set()
    found = False
    for i in range(len(maze)):
        if found:
            break
        for j in range(len(maze[0])):
            if maze[i][j] == MAZE.PATH:
                queue.append((i, j))
                visited.add((i, j))
                found = True
                break
    while queue:
        x, y = queue.popleft()
        for dx, dy in MAZE.DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(maze) and 0 <= ny < len(maze[0]) \
                    and maze[nx][ny] == MAZE.PATH:
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    for i in range(len(maze)):
        for j in range(len(maze[0])):
            if maze[i][j] == MAZE.PATH and (i, j) not in visited:
                return False
    return True


# ── 内部工具函数 ──────────────────────────────────────

def _compute_depths(maze, start, cells):
    depth = {}
    queue = deque([start])
    depth[start] = 0
    while queue:
        x, y = queue.popleft()
        for dx, dy in MAZE.DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < maze.n and 0 <= ny < maze.n:
                if maze.get_cell(nx, ny) != MAZE.WALL and (nx, ny) not in depth:
                    depth[(nx, ny)] = depth[(x, y)] + 1
                    queue.append((nx, ny))
    return depth


def _count_walkable_neighbors(maze, pos):
    x, y = pos
    count = 0
    for dx, dy in MAZE.DIRECTIONS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < maze.n and 0 <= ny < maze.n:
            if maze.get_cell(nx, ny) != MAZE.WALL:
                count += 1
    return count


def _find_spine(maze, start, end, path_cells):
    """BFS 找起点→终点主干路径"""
    path_set = set(path_cells)
    parent = {}
    queue = deque([start])
    parent[start] = None
    while queue:
        u = queue.popleft()
        x, y = u
        for dx, dy in MAZE.DIRECTIONS:
            nx, ny = x + dx, y + dy
            if (nx, ny) in path_set and (nx, ny) not in parent:
                parent[(nx, ny)] = u
                if (nx, ny) == end:
                    spine = [end]
                    node = end
                    while parent[node] is not None:
                        node = parent[node]
                        spine.append(node)
                    return spine
                queue.append((nx, ny))
    return []


# ── 资源放置（贪心挑战版）─────────────────────────────

def place_resources(maze):
    """在通路上放置资源（4 金币 + 5 陷阱 + 1 BOSS）
       陷阱分层：主干 2 + 歧路 2 + 深层 1"""
    n = maze.n
    start = getattr(maze, 'start', (1, 1))
    end = getattr(maze, 'end', start)

    path_cells = []
    for i in range(n):
        for j in range(n):
            if maze.get_cell(i, j) == MAZE.PATH:
                path_cells.append((i, j))
    total = len(path_cells)
    if total == 0:
        return

    depth = _compute_depths(maze, start, path_cells)
    max_d = max(depth.values()) if depth else 1

    shallow = [p for p in path_cells if depth.get(p, 0) < max_d * 0.3]
    mid = [p for p in path_cells if max_d * 0.3 <= depth.get(p, 0) < max_d * 0.65]
    deep = [p for p in path_cells if depth.get(p, 0) >= max_d * 0.65]
    junctions = [p for p in path_cells if _count_walkable_neighbors(maze, p) > 2]
    dead_ends = [p for p in path_cells if _count_walkable_neighbors(maze, p) == 1]
    spine = _find_spine(maze, start, end, path_cells)

    _random.shuffle(shallow)
    _random.shuffle(mid)
    _random.shuffle(deep)

    placed = set()
    coin_cnt = 0
    trap_cnt = 0
    boss_cnt = 0

    MAX_COINS = 4
    MAX_TRAPS = 5
    MAX_BOSS = 1

    # 诱饵金币（浅中层）
    for p in mid + shallow:
        if coin_cnt >= MAX_COINS // 2:
            break
        maze.set_cell(p[0], p[1], MAZE.COIN)
        coin_cnt += 1
        placed.add(p)

    # 陷阱 — 主干（2个，必经）
    _random.shuffle(spine)
    for p in spine:
        if trap_cnt >= 2:
            break
        if p not in placed and p != start and p != end:
            maze.set_cell(p[0], p[1], MAZE.TRAP)
            trap_cnt += 1
            placed.add(p)

    # 陷阱 — 歧路（2个，可绕）
    junc_shuffled = junctions[:]
    _random.shuffle(junc_shuffled)
    for p in junc_shuffled:
        if trap_cnt >= 4:
            break
        if p not in placed:
            maze.set_cell(p[0], p[1], MAZE.TRAP)
            trap_cnt += 1
            placed.add(p)

    # 陷阱 — 深层（1个，惩罚深入）
    deep_shuffled = deep[:]
    _random.shuffle(deep_shuffled)
    for p in deep_shuffled:
        if trap_cnt >= MAX_TRAPS:
            break
        if p not in placed:
            maze.set_cell(p[0], p[1], MAZE.TRAP)
            trap_cnt += 1
            placed.add(p)

    # 深层金币（分支末端）
    for p in deep:
        if coin_cnt >= MAX_COINS:
            break
        if p not in placed:
            maze.set_cell(p[0], p[1], MAZE.COIN)
            coin_cnt += 1
            placed.add(p)

    # BOSS（最深死胡同）
    if dead_ends:
        dead_ends_sorted = sorted(dead_ends, key=lambda p: depth.get(p, 0), reverse=True)
        for p in dead_ends_sorted:
            if boss_cnt >= MAX_BOSS:
                break
            maze.set_cell(p[0], p[1], MAZE.BOSS)
            boss_cnt += 1


# ── 迷宫分析 ──────────────────────────────────────────

def analyze_maze(maze):
    grid = maze.maze
    n = maze.n
    start = getattr(maze, 'start', (1, 1))
    end = getattr(maze, 'end', start)
    WALK = {MAZE.PATH, MAZE.START, MAZE.END, MAZE.COIN, MAZE.TRAP, MAZE.BOSS}

    walkable = [(i, j) for i in range(n) for j in range(n) if grid[i][j] in WALK]
    dead_ends = sum(1 for p in walkable if _count_walkable_neighbors(maze, p) == 1)
    branches = [_count_walkable_neighbors(maze, p) - 1 for p in walkable
                if _count_walkable_neighbors(maze, p) > 1]
    avg_branch = round(sum(branches) / len(branches), 2) if branches else 0

    dist = {start: 0}
    queue = deque([start])
    max_depth = 0
    while queue:
        x, y = queue.popleft()
        for dx, dy in MAZE.DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < n and grid[nx][ny] in WALK and (nx, ny) not in dist:
                dist[(nx, ny)] = dist[(x, y)] + 1
                queue.append((nx, ny))
                if dist[(nx, ny)] > max_depth:
                    max_depth = dist[(nx, ny)]
    path_length = dist.get(end, -1)

    return {
        "deadEnds": dead_ends,
        "avgBranching": avg_branch,
        "pathLength": path_length,
        "maxDepth": max_depth,
        "walkableCount": len(walkable),
    }
