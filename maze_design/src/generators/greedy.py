# 贪心（最小生成树 / Kruskal）迷宫生成
# 将所有墙随机洗牌，用并查集连接房间

import random
from maze import WALL, PATH, START, END
from utils import place_resources, pick_edge_positions


class _UnionFind:
    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def generate_maze_greedy(maze, on_step=None):
    n = maze.n
    if n % 2 == 1:
        max_room = n - 2
    else:
        max_room = n - 3

    # 全墙
    for i in range(n):
        for j in range(n):
            maze.set_cell(i, j, WALL)

    # 所有房间格设为通路
    rooms = []
    uf = _UnionFind()
    for i in range(1, max_room + 1, 2):
        for j in range(1, max_room + 1, 2):
            maze.set_cell(i, j, PATH)
            rooms.append((i, j))

    # 收集所有可打通的墙（偶数坐标，位于两个房间之间）
    walls = []
    for i in range(1, max_room + 1, 2):
        for j in range(1, max_room + 1, 2):
            # 右边的墙
            if j + 2 <= max_room:
                walls.append(((i, j + 1), (i, j), (i, j + 2)))
            # 下方的墙
            if i + 2 <= max_room:
                walls.append(((i + 1, j), (i, j), (i + 2, j)))

    random.shuffle(walls)

    step_counter = 0
    for wall_pos, room_a, room_b in walls:
        if uf.union(room_a, room_b):
            wx, wy = wall_pos
            maze.set_cell(wx, wy, PATH)
            step_counter += 1
            if on_step and step_counter % 3 == 0:
                on_step(maze, wx, wy)

    # 偶数补偿
    if n % 2 == 0:
        for i in range(1, max_room + 1, 2):
            if maze.get_cell(i, max_room) == PATH:
                maze.set_cell(i, max_room + 1, PATH)
            if maze.get_cell(max_room, i) == PATH:
                maze.set_cell(max_room + 1, i, PATH)

    (startx, starty), (endx, endy) = pick_edge_positions(maze)
    maze.set_start(startx, starty)
    maze.set_end(endx, endy)
    place_resources(maze)

    if on_step:
        on_step(maze, endx, endy)

    return maze
