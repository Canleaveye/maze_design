# 回溯法 / DFS 迷宫生成

import random
from maze import WALL, PATH, START, END

def generate_maze_backtrack_dfs(maze):
    n = maze.n

    # 1. 根据奇偶确定起始偏移
    offset = n % 2          # 奇数→1（有外围墙），偶数→0（贴边）
    sx = sy = offset        # 起点坐标
    ex = ey = n - 2         # 终点坐标（始终是合法格子）

    # 2. 初始化全墙
    for i in range(n):
        for j in range(n):
            maze.set_cell(i, j, WALL)

    # 3. 设起点为通路
    maze.set_cell(sx, sy, PATH)

    # 4. 访问集合 + 栈（用于回溯）
    visited = set()
    visited.add((sx, sy))
    stack = [(sx, sy)]

    # 5. DFS 挖路主循环
    while stack:
        x, y = stack[-1]  # 当前位置（栈顶）

        # 收集跳 2 步可达的未访问格子
        neighbors = []
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nx, ny = x + dx, y + dy
            if offset <= nx <= n - 2 and offset <= ny <= n - 2:
                if (nx, ny) not in visited:
                    neighbors.append((nx, ny))

        if neighbors:
            # 随机选一个挖过去
            nx, ny = random.choice(neighbors)
            # 打通中间的墙
            mx, my = (x + nx) // 2, (y + ny) // 2
            maze.set_cell(mx, my, PATH)
            # 打通目标格
            maze.set_cell(nx, ny, PATH)
            visited.add((nx, ny))
            stack.append((nx, ny))
        else:
            # 死路 → 回溯
            stack.pop()

    # 6. 设置起点和终点
    maze.set_start(sx, sy)
    maze.set_end(ex, ey)

    return maze
