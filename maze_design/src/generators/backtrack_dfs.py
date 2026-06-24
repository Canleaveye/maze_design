# 回溯法 / DFS 迷宫生成
# 零空间浪费 + 完美迷宫（唯一通路） + 适配任意奇偶尺寸
# 支持 on_step 回调用于可视化

import random
from maze import WALL, PATH, START, END
from utils import place_resources_greedy_challenge


def generate_maze_backtrack_dfs(maze, on_step=None):
    """
    on_step: 可选回调，每次挖墙后调用 on_step(maze, x, y)
    """
    n = maze.n

    if n % 2 == 1:
        max_room = n - 2
    else:
        max_room = n - 3

    startx = starty = 1
    endx = endy = max_room

    for i in range(n):
        for j in range(n):
            maze.set_cell(i, j, WALL)

    maze.set_cell(startx, starty, PATH)
    visited = {(startx, starty)}
    stack = [(startx, starty)]

    if on_step:
        on_step(maze, startx, starty)

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

    # ——— 先设起点终点，再放资源（避免 BOSS 被覆盖）
    maze.set_start(startx, starty)
    maze.set_end(endx, endy)
    place_resources_greedy_challenge(maze)

    if on_step:
        on_step(maze, endx, endy)

    return maze
