# 回溯法生成迷宫

import random
from maze import WALL, PATH, START, END
from utils import place_resources, pick_edge_positions


def generate_maze_backtrack_dfs(maze, on_step=None):
    n = maze.n

    if n % 2 == 1:
        max_room = n - 2
    else:
        max_room = n - 3

    seed_x = seed_y = 1
    # 先把边缘格设墙
    for i in range(n):
        for j in range(n):
            maze.set_cell(i, j, WALL)

    maze.set_cell(seed_x, seed_y, PATH)
    visited = {(seed_x, seed_y)}
    stack = [(seed_x, seed_y)]

    # 用于可视化
    if on_step:
        on_step(maze, seed_x, seed_y)

    while stack:
        # 栈顶元素
        x, y = stack[-1]
        neighbors = []
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            # 把符合条件的邻居加入列表
            nx, ny = x + dx, y + dy
            if 1 <= nx <= max_room and 1 <= ny <= max_room:
                if (nx, ny) not in visited:
                    neighbors.append((nx, ny))

        if neighbors:
            # 随机选择一个邻居
            nx, ny = random.choice(neighbors)
            # 把当前单元格和邻居之间的墙打通
            maze.set_cell((x + nx) // 2, (y + ny) // 2, PATH)
            maze.set_cell(nx, ny, PATH)
            # 往下深度优先搜索
            visited.add((nx, ny))
            stack.append((nx, ny))
            # 可视化接口
            if on_step:
                # 显示当前单元格和邻居打通的过程
                on_step(maze, nx, ny)
        else:
            stack.pop()

    if n % 2 == 0:
        # 扩展迷宫边缘偶数行列
        for i in range(1, max_room + 1, 2):
            if maze.get_cell(i, max_room) == PATH:
                maze.set_cell(i, max_room + 1, PATH)
            if maze.get_cell(max_room, i) == PATH:
                maze.set_cell(max_room + 1, i, PATH)

    # 起点终点设在边缘
    (startx, starty), (endx, endy) = pick_edge_positions(maze)
    maze.set_start(startx, starty)
    maze.set_end(endx, endy)
    # 放置资源
    place_resources(maze)

    # 可视化展示生成的迷宫
    if on_step:
        on_step(maze, endx, endy)

    return maze
