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

# 