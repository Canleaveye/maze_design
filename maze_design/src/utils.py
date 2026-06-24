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
def place_resources(maze, coin_ratio=0.25, trap_ratio=0.08, boss_count=1):
    """
    在已有 PATH 格子上放置资源（应在 set_start/set_end 之后调用）

    参数:
        maze:        Maze 对象
        coin_ratio:  金币占通路格比例 (默认 25%)
        trap_ratio:  陷阱占通路格比例 (默认 8%)
        boss_count:  BOSS 数量 (默认 1)
    """
    import random as _random
    n = maze.n

    # 收集所有 PATH 格子（START/END 已不是 PATH，自动排除）
    path_cells = []
    for i in range(n):
        for j in range(n):
            if maze.get_cell(i, j) == MAZE.PATH:
                path_cells.append((i, j))

    total = len(path_cells)
    if total == 0:
        return

    _random.shuffle(path_cells)

    coin_count = max(1, int(total * coin_ratio))
    trap_count = max(1, int(total * trap_ratio))
    idx = 0

    for _ in range(coin_count):
        if idx >= len(path_cells):
            break
        x, y = path_cells[idx]
        maze.set_cell(x, y, MAZE.COIN)
        idx += 1

    for _ in range(trap_count):
        if idx >= len(path_cells):
            break
        x, y = path_cells[idx]
        maze.set_cell(x, y, MAZE.TRAP)
        idx += 1

    boss_candidates = path_cells[idx:]
    if boss_candidates and boss_count > 0:
        boss_candidates.sort(
            key=lambda p: abs(p[0] - 1) + abs(p[1] - 1), reverse=True
        )
        for k in range(min(boss_count, len(boss_candidates))):
            x, y = boss_candidates[k]
            maze.set_cell(x, y, MAZE.BOSS)