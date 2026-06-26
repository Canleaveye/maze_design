# 辅助工具函数模块

import maze as MAZE
from collections import deque
import random as _random


# 验证生成的迷宫无孤立区域并存在唯一完美通路
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


# 计算迷宫中每个可行走单元格距离起点的步数
def _compute_depths(maze, start):
    # 结果字典，键：单元格坐标，值：距离起点的步数
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

# 判断一个单元格的可行走邻居格子数
def _count_walkable_neighbors(maze, pos):
    x, y = pos
    count = 0
    for dx, dy in MAZE.DIRECTIONS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < maze.n and 0 <= ny < maze.n:
            if maze.get_cell(nx, ny) != MAZE.WALL:
                count += 1
    return count

# 寻找迷宫中从起点到终点的路径，用于资源放置策略
def _find_spine(maze, start, end):
    # 记录迷宫中能走的单元格
    WALK = {MAZE.PATH, MAZE.START, MAZE.END}
    queue = deque([start])
    # 每个单元格的父节点，用于回溯路径
    parent = {start: None}
    while queue:
        u = queue.popleft()
        x, y = u
        for dx, dy in MAZE.DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < maze.n and 0 <= ny < maze.n:
                val = maze.get_cell(nx, ny)
                """如果邻居是可走的且未被访问过，则记录父节点并加入队列
                    不加重复的避免死循环，同时保证找到的路径是最短的"""
                if val in WALK and (nx, ny) not in parent:
                    parent[(nx, ny)] = u
                    if (nx, ny) == end:
                        spine = [end]
                        node = end
                        while parent[node] is not None:
                            node = parent[node]
                            # 回溯路径，直到回到起点
                            spine.append(node)
                        return spine
                    queue.append((nx, ny))
    # 没有找到路径,说明生成的迷宫不连通，返回空列表
    return []


# 资源放置函数（固定数量：4金币 / 5陷阱 / 1BOSS

def place_resources(maze):
    """Place 4 coins + 5 traps + 1 BOSS on PATH cells.
       Traps layered: 2 on spine, 2 at junctions, 1 deep."""
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

    depth = _compute_depths(maze, start)
    max_d = max(depth.values()) if depth else 1

    shallow = [p for p in path_cells if depth.get(p, 0) < max_d * 0.3]
    mid     = [p for p in path_cells if max_d * 0.3 <= depth.get(p, 0) < max_d * 0.65]
    deep    = [p for p in path_cells if depth.get(p, 0) >= max_d * 0.65]
    junctions = [p for p in path_cells if _count_walkable_neighbors(maze, p) > 2]
    dead_ends = [p for p in path_cells if _count_walkable_neighbors(maze, p) == 1]
    spine = _find_spine(maze, start, end)

    _random.shuffle(shallow)
    _random.shuffle(mid)
    _random.shuffle(deep)

    placed = set()
    coin_cnt = 0
    trap_cnt = 0
    boss_cnt = 0

    # 按迷宫规模决定资源数量
    room_count = ((n + 1) // 2) ** 2  # 房间格数量
    if n <= 7:
        MAX_COINS, MAX_TRAPS = 3, 3
    elif n <= 15:
        MAX_COINS, MAX_TRAPS = 9, 13
    else:
        MAX_COINS, MAX_TRAPS = max(12, room_count // 5), max(16, room_count // 3)
    MAX_BOSS = 1

    # bait coins (shallow/mid)
    for p in mid + shallow:
        if coin_cnt >= MAX_COINS // 2:
            break
        maze.set_cell(p[0], p[1], MAZE.COIN)
        coin_cnt += 1
        placed.add(p)

    # spine traps (unavoidable, but limited)
    _spine_trap_count = min(2, MAX_TRAPS // 3)
    _random.shuffle(spine)
    for p in spine:
        if trap_cnt >= _spine_trap_count:
            break
        if p not in placed and p != start and p != end:
            maze.set_cell(p[0], p[1], MAZE.TRAP)
            trap_cnt += 1
            placed.add(p)

    # junction traps (avoidable, fill most of remaining)
    _junction_trap_count = MAX_TRAPS - 1  # leave at least 1 for deep
    junc_shuffled = junctions[:]
    _random.shuffle(junc_shuffled)
    for p in junc_shuffled:
        if trap_cnt >= _junction_trap_count:
            break
        if p not in placed:
            maze.set_cell(p[0], p[1], MAZE.TRAP)
            trap_cnt += 1
            placed.add(p)

    # deep trap (at least 1, punishment for deep exploration)
    deep_shuffled = deep[:]
    _random.shuffle(deep_shuffled)
    for p in deep_shuffled:
        if trap_cnt >= MAX_TRAPS:
            break
        if p not in placed:
            maze.set_cell(p[0], p[1], MAZE.TRAP)
            trap_cnt += 1
            placed.add(p)

    # deep coins (branch ends)
    for p in deep:
        if coin_cnt >= MAX_COINS:
            break
        if p not in placed:
            maze.set_cell(p[0], p[1], MAZE.COIN)
            coin_cnt += 1
            placed.add(p)

    # BOSSes: near spine but not on it (high-traffic branches, can be bypassed)
    spine_set = set(spine)
    near_spine = []
    for p in path_cells:
        if p in spine_set or p == start or p == end:
            continue
        # compute distance to nearest spine cell
        for sp in spine:
            if abs(p[0]-sp[0]) + abs(p[1]-sp[1]) <= 3:
                near_spine.append(p)
                break
    _random.shuffle(near_spine)
    for p in near_spine:
        if boss_cnt >= MAX_BOSS:
            break
        if p not in placed:
            maze.set_cell(p[0], p[1], MAZE.BOSS)
            boss_cnt += 1
            placed.add(p)


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
