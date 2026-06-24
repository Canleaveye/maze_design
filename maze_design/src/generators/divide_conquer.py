# 分治递归迷宫生成
# 标准递归分割：在房间网格上递归加墙 + 开单门

import random
from maze import WALL, PATH, START, END
from utils import place_resources_greedy_challenge
from collections import deque


def _find_furthest_cell(maze, start):
    n = maze.n
    queue = deque([start])
    dist = {start: 0}
    furthest, max_d = start, 0
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


def generate_maze_divide_conquer(maze, on_step=None):
    n = maze.n
    if n % 2 == 1:
        max_room = n - 2
    else:
        max_room = n - 3

    # 全墙
    for i in range(n):
        for j in range(n):
            maze.set_cell(i, j, WALL)

    # 把所有房间格 (奇数坐标) 设为通路
    for i in range(1, max_room + 1, 2):
        for j in range(1, max_room + 1, 2):
            maze.set_cell(i, j, PATH)

    def _notify():
        if on_step:
            on_step(maze, 1, 1)

    # 房间坐标 → 矩阵坐标: room (r, c) → maze (1+2r, 1+2c)
    # rooms_w = rooms_h = (max_room + 1) // 2
    rooms_w = (max_room + 1) // 2
    rooms_h = (max_room + 1) // 2

    def divide(r1, c1, r2, c2):
        w = c2 - c1 + 1
        h = r2 - r1 + 1
        if w <= 1 and h <= 1:
            return

        # 只有横向可切
        if w <= 1:
            wr = random.randint(r1 + 1, r2)
            wall_row = 1 + 2 * (wr - 1) + 1
            for room_c in range(c1, c2 + 1):
                mc = 1 + 2 * room_c
                maze.set_cell(wall_row, mc, WALL)
            door_c = random.randint(c1, c2)
            door_mc = 1 + 2 * door_c
            maze.set_cell(wall_row, door_mc, PATH)
            _notify()
            divide(r1, c1, wr - 1, c2)
            divide(wr, c1, r2, c2)

        # 只有竖向可切
        elif h <= 1:
            wc = random.randint(c1 + 1, c2)
            wall_col = 1 + 2 * (wc - 1) + 1
            for room_r in range(r1, r2 + 1):
                mr = 1 + 2 * room_r
                maze.set_cell(mr, wall_col, WALL)
            door_r = random.randint(r1, r2)
            door_mr = 1 + 2 * door_r
            maze.set_cell(door_mr, wall_col, PATH)
            _notify()
            divide(r1, c1, r2, wc - 1)
            divide(r1, wc, r2, c2)

        # 双向可选
        elif w > h or (w == h and random.random() < 0.5):
            wc = random.randint(c1 + 1, c2)
            wall_col = 1 + 2 * (wc - 1) + 1
            for room_r in range(r1, r2 + 1):
                mr = 1 + 2 * room_r
                maze.set_cell(mr, wall_col, WALL)
            door_r = random.randint(r1, r2)
            door_mr = 1 + 2 * door_r
            maze.set_cell(door_mr, wall_col, PATH)
            _notify()
            divide(r1, c1, r2, wc - 1)
            divide(r1, wc, r2, c2)
        else:
            wr = random.randint(r1 + 1, r2)
            wall_row = 1 + 2 * (wr - 1) + 1
            for room_c in range(c1, c2 + 1):
                mc = 1 + 2 * room_c
                maze.set_cell(wall_row, mc, WALL)
            door_c = random.randint(c1, c2)
            door_mc = 1 + 2 * door_c
            maze.set_cell(wall_row, door_mc, PATH)
            _notify()
            divide(r1, c1, wr - 1, c2)
            divide(wr, c1, r2, c2)

    divide(0, 0, rooms_h - 1, rooms_w - 1)

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
