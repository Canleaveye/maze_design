# 贪心 AI 玩家 —— 3×3 视野 + 性价比评分 + 回溯探索
# 记住见过的资源，每步按"价值/距离"择优，无资源时向终点/未探索区走

from collections import deque
from maze import WALL, PATH, START, END, COIN, TRAP, BOSS, DIRECTIONS, COIN_VALUE, TRAP_VALUE

WALKABLE_SET = {PATH, START, END, COIN, TRAP, BOSS}


class GreedyPlayer:
    def __init__(self, maze, vision_range=1):
        self.maze = maze
        self.grid = maze.maze
        self.n = maze.n
        self.vision = vision_range
        self.pos = maze.start
        self.end = maze.end
        self.collected = 0
        self.steps = 0
        self.path = [self.pos]
        self.memory = set()          # 见过的所有 Walkable 格子
        self.resources_seen = {}     # 见过的资源 {pos: value}
        self.collected_at = set()    # 已拾取（避免重复计数）
        self.traps_hit = set()
        self.explored = set()        # 已经访问过的格子
        self._build_adj()

    def _build_adj(self):
        self.adj = {}
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] in WALKABLE_SET:
                    nb = []
                    for dx, dy in DIRECTIONS:
                        nx, ny = i + dx, j + dy
                        if 0 <= nx < self.n and 0 <= ny < self.n:
                            if self.grid[nx][ny] in WALKABLE_SET:
                                nb.append((nx, ny))
                    self.adj[(i, j)] = nb

    def _bfs_dist(self, a, b):
        if a == b:
            return 0
        q = deque([a])
        d = {a: 0}
        while q:
            u = q.popleft()
            for v in self.adj.get(u, []):
                if v not in d:
                    d[v] = d[u] + 1
                    if v == b:
                        return d[v]
                    q.append(v)
        return float('inf')

    def _first_step_to(self, target):
        if self.pos == target:
            return target
        q = deque([self.pos])
        parent = {self.pos: None}
        while q:
            u = q.popleft()
            for v in self.adj.get(u, []):
                if v not in parent:
                    parent[v] = u
                    if v == target:
                        node = target
                        while parent[node] != self.pos:
                            node = parent[node]
                        return node
                    q.append(v)
        return self.pos

    def _scan(self):
        """3×3 视野扫描并更新记忆"""
        x, y = self.pos
        for dx in range(-self.vision, self.vision + 1):
            for dy in range(-self.vision, self.vision + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.n and 0 <= ny < self.n:
                    if self.grid[nx][ny] != WALL:
                        self.memory.add((nx, ny))
                        v = self.grid[nx][ny]
                        if v == COIN and (nx, ny) not in self.collected_at:
                            self.resources_seen[(nx, ny)] = COIN_VALUE
                        elif v == TRAP and (nx, ny) not in self.traps_hit:
                            self.resources_seen[(nx, ny)] = TRAP_VALUE

    def _best_target(self):
        """按 max(value/distance) 从记忆中选最优目标，
           距离越近价值越高的优先"""
        best = None
        best_score = -1e9
        for target, value in self.resources_seen.items():
            if target in self.collected_at or target in self.traps_hit:
                continue
            dist = self._bfs_dist(self.pos, target)
            if dist == 0 or dist > 500:
                continue
            score = value / dist
            if score > best_score:
                best_score = score
                best = target
        return best

    def _nearest_unexplored(self):
        """找最近的未探索 walkable 格子"""
        candidates = [p for p in self.memory if p not in self.explored]
        if not candidates:
            return None
        best = None
        best_dist = float('inf')
        for c in candidates:
            d = self._bfs_dist(self.pos, c)
            if d < best_dist:
                best_dist = d
                best = c
        return best

    def _collect(self, pos):
        val = self.grid[pos[0]][pos[1]]
        if val == COIN and pos not in self.collected_at:
            self.collected += COIN_VALUE
            self.collected_at.add(pos)
        elif val == TRAP and pos not in self.traps_hit:
            self.collected += TRAP_VALUE
            self.traps_hit.add(pos)

    def step(self):
        self._scan()
        self.explored.add(self.pos)

        # 终点就在眼前 → 进去
        if self._bfs_dist(self.pos, self.end) <= 1:
            target = self.end
        else:
            target = self._best_target()

        if target is None:
            # 无资源目标 → 探索未访问区 / 走向终点
            unexplored = self._nearest_unexplored()
            if unexplored:
                target = unexplored
            else:
                target = self.end

        nxt = self._first_step_to(target)
        if nxt == self.pos:
            return False

        self.pos = nxt
        self.steps += 1
        self.path.append(self.pos)
        self._collect(self.pos)
        self.resources_seen.pop(self.pos, None)
        return self.pos != self.end

    def play(self, max_steps=20000):
        while self.pos != self.end and self.steps < max_steps:
            if not self.step():
                break
        return self.collected, self.steps, self.path

    def efficiency(self):
        return self.collected / self.steps if self.steps else 0
