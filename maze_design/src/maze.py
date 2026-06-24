# 迷宫矩阵编码常量
# 墙
WALL = 1 
# 路径
PATH = 0
# 入口
START = 2
# 出口
END = 3
# 金币
COIN = 4
# 陷阱
TRAP = 5
# BOSS
BOSS = 6

# 资源价值
COIN_VALUE = 50
TRAP_VALUE = -30

# 移动方向向量
DIRECTIONS = [
    (-1,0), # 上
    (1,0),  # 下
    (0,-1), # 左
    (0,1)   # 右
]

# 迷宫类
class Maze:
    # 初始化迷宫
    def __init__(self,n):
        # 设置迷宫规模
        self.n = n
        self.maze = [[WALL for i in range(n)]for j in range(n)]
    
    def set_start(self, x, y):
        self.maze[x][y] = START
        self.start = (x, y)
    
    def set_end(self,x,y):
        self.maze[x][y] = END
        self.end = (x,y)
    
    def set_cell(self,x,y,val):
        self.maze[x][y] = val

    def get_cell(self,x,y) -> int:
        return self.maze[x][y]

    def to_json_matrix(self):
        """转换为 JSON 输出格式的字符矩阵"""
        SYMBOL = {WALL: '#', PATH: ' ', START: 'S', END: 'E',
                  COIN: 'G', TRAP: 'T', BOSS: 'B'}
        return [[SYMBOL.get(self.maze[i][j], '?')
                 for j in range(self.n)] for i in range(self.n)]