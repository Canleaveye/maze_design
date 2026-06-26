# 回溯法 / DFS 迷宫生成
# 零空间浪费 + 完美迷宫（唯一通路） + 适配任意奇偶尺寸
# 支持 on_step 回调用于可视化

import random
from maze import WALL, PATH, START, END
from utils import place_resources, pick_edge_positions


def generate_maze_backtrack_dfs(maze, on_step=None):
    n = maze.n

    if n % 2 == 1:
        max_room = n - 2
    else:
        max_room = n - 3

    # DFS 起点固定从 (1,1) 开始挖路
    seed_x = seed_y = 1

    for i in range(n):
        for j in range(n):
            maze.set_cell(i, j, WALL)

    maze.set_cell(seed_x, seed_y, PATH)
    visited = {(seed_x, seed_y)}
    stack = [(seed_x, seed_y)]

    if on_step:
        on_step(maze, seed_x, seed_y)

    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nx, ny = x + dx, y + dy
            if 1 <= nx <= max_room and 1 <= ny <= max_room:
                if (nx, ny) not in visited:
                    neighbors.append((nx, ny))

        if neighbors:
            nx, ny = random.choice(neighbors)
            maze.set_cell((x + nx) // 2, (y + ny) // 2, PATH)
            maze.set_cell(nx, ny, PATH)
            visited.add((nx, ny))
            stack.append((nx, ny))
            if on_step:
                on_step(maze, nx, ny)
        else:
            stack.pop()

    if n % 2 == 0:
        for i in range(1, max_room + 1, 2):
            if maze.get_cell(i, max_room) == PATH:
                maze.set_cell(i, max_room + 1, PATH)
            if maze.get_cell(max_room, i) == PATH:
                maze.set_cell(max_room + 1, i, PATH)

    # 起点终点放在边缘（模拟进出迷宫）
    (startx, starty), (endx, endy) = pick_edge_positions(maze)
    maze.set_start(startx, starty)
    maze.set_end(endx, endy)
    place_resources(maze)

    if on_step:
        on_step(maze, endx, endy)

    return maze
