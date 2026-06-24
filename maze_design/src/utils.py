# 辅助工具函数模块

import maze as MAZE
from collections import deque

# 检查迷宫是否连通函数
def is_connected(maze):
    # 这里用广度优先的思想
    queue = deque()
    visited = set()
    found = False
    for i in range(len(maze)):
        if found:
            break
        for j in range(len(maze[0])):
            # 将迷宫格子加入队列
            if maze[i][j] == MAZE.PATH:
                queue.append((i,j))
                visited.add((i,j))
                found = True
                break
    while queue:
        x,y = queue.popleft()
        for dx,dy in MAZE.DIRECTIONS:
            nx = x + dx
            ny = y + dy
            if nx >=0 and nx < len(maze) and ny >=0 and ny < len(maze[0]) \
                and maze[nx][ny] == MAZE.PATH:
                if (nx,ny) not in visited:
                    visited.add((nx,ny))
                    queue.append((nx,ny))

    # 检查是否所有的路径格子都被访问过
    for i in range(len(maze)):
        for j in range(len(maze[0])):
            if maze[i][j] == MAZE.PATH and (i,j) not in visited:
                return False
    return True


# 在迷宫通路格子上随机放置资源（金币、陷阱、BOSS）
# v2: 偏向深度分布 —— 金币在深处，陷阱在中层，BOSS 在最深死路
def place_resources(maze, coin_ratio=0.25, trap_ratio=0.08, boss_count=1):
    """
    应有 PATH 格子上放置资源（应在 set_start/set_end 之后调用）
    按 BFS 深度加权，让金币集中在迷宫深处（引人深入），陷阱偏中段。
    """
    import random as _random
    n = maze.n

    path_cells = []
    for i in range(n):
        for j in range(n):
            if maze.get_cell(i, j) == MAZE.PATH:
                path_cells.append((i, j))

    total = len(path_cells)
    if total == 0:
        return

    # 计算每个通路格的 BFS 深度（从起点出发）
    start = getattr(maze, 'start', (1, 1))
    depth = _compute_depths(maze, start, path_cells)

    # 按深度降序排列（深处的优先）
    path_cells.sort(key=lambda p: depth.get(p, 0), reverse=True)

    coin_count = max(1, int(total * coin_ratio))
    trap_count = max(1, int(total * trap_ratio))

    # 金币：从最深往前取（深度越深概率越高）
    coin_pool = path_cells[:int(total * 0.7)]  # 取前 70% 深度最大者
    _random.shuffle(coin_pool)
    for k in range(min(coin_count, len(coin_pool))):
        x, y = coin_pool[k]
        maze.set_cell(x, y, MAZE.COIN)

    # 陷阱：从中层取（避免开头和深末）
    start_mid = max(1, total // 4)
    end_mid = total - total // 4
    trap_pool = path_cells[start_mid:end_mid]
    _random.shuffle(trap_pool)
    for k in range(min(trap_count, len(trap_pool))):
        x, y = trap_pool[k]
        maze.set_cell(x, y, MAZE.TRAP)

    # BOSS：最深区的死胡同叶子节点
    # 在已放置 coin/trap 后，找剩余最深叶子
    remaining = [p for p in path_cells
                 if maze.get_cell(p[0], p[1]) == MAZE.PATH]
    if remaining and boss_count > 0:
        # 叶子 = 只有 1 个 walkable 邻居
        leaves = [_ for _ in remaining if _count_walkable_neighbors(maze, _) == 1]
        if not leaves:
            leaves = remaining
        leaves.sort(key=lambda p: depth.get(p, 0), reverse=True)
        for k in range(min(boss_count, len(leaves))):
            x, y = leaves[k]
            maze.set_cell(x, y, MAZE.BOSS)


def _compute_depths(maze, start, cells):
    """BFS 计算所有通路格相对起点的深度"""
    from collections import deque
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
    """统计某格子的可走邻居数"""
    x, y = pos
    count = 0
    for dx, dy in MAZE.DIRECTIONS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < maze.n and 0 <= ny < maze.n:
            if maze.get_cell(nx, ny) != MAZE.WALL:
                count += 1
    return count