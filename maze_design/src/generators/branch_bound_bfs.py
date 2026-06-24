# 分支限界 / BFS 迷宫生成
# 用队列扩展前沿，BFS 随机选边挖路

import random
from collections import deque
from maze import WALL, PATH, START, END
from utils import place_resources_greedy_challenge


def _find_furthest_cell(maze, start):
    n = maze.n
    queue = deque([start])
    dist = {start: 0}
    furthest = start
    max_d = 0
    while queue:
        x, y = queue.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < n:
                if maze.get_cell(nx, ny) != WALL and (nx, ny) not in dist:
                    dist[(nx, ny)] = dist[(x, y)] + 1
                    queue.append((nx, ny))
                    if dist[(nx, ny)] > max_d:
                        max_d = dist[(nx, ny)]
                        furthest = (nx, ny)
    return furthest


def generate_maze_branch_bound_bfs(maze, on_step=None):
    n = maze.n
    if n % 2 == 1:
        max_room = n - 2
    else:
        max_room = n - 3

    # 全墙
    for i in range(n):
        for j in range(n):
            maze.set_cell(i, j, WALL)

    # 随机选起点
    sx = random.randrange(1, max_room + 1, 2)
    sy = random.randrange(1, max_room + 1, 2)
    maze.set_cell(sx, sy, PATH)

    visited = {(sx, sy)}
    frontier = deque([(sx, sy)])

    if on_step:
        on_step(maze, sx, sy)

    while frontier:
        x, y = frontier.popleft()

        # 收集未访问邻居
        unvisited = []
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nx, ny = x + dx, y + dy
            if 1 <= nx <= max_room and 1 <= ny <= max_room:
                if (nx, ny) not in visited:
                    unvisited.append((nx, ny))

        if unvisited:
            # 将所有未访问邻居加入前沿，随机连接一个
            random.shuffle(unvisited)
            for nx, ny in unvisited:
                if (nx, ny) not in visited:
                    # 打通墙
                    maze.set_cell((x + nx) // 2, (y + ny) // 2, PATH)
                    maze.set_cell(nx, ny, PATH)
                    visited.add((nx, ny))
                    frontier.append((nx, ny))
                    if on_step:
                        on_step(maze, nx, ny)

    # 偶数补偿
    if n % 2 == 0:
        for i in range(1, max_room + 1, 2):
            if maze.get_cell(i, max_room) == PATH:
                maze.set_cell(i, max_room + 1, PATH)
            if maze.get_cell(max_room, i) == PATH:
                maze.set_cell(max_room + 1, i, PATH)

    startx = starty = 1
    endx, endy = _find_furthest_cell(maze, (startx, starty))

    maze.set_start(startx, starty)
    maze.set_end(endx, endy)
    place_resources_greedy_challenge(maze)

    if on_step:
        on_step(maze, endx, endy)

    return maze
