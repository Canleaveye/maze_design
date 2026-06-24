# 迷宫可视化模块

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from maze import WALL, PATH, START, END, COIN, TRAP, BOSS

# 配置中文字体
try:
    matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False
except Exception:
    pass

# 颜色映射
COLORMAP = {
    WALL:  '#1a1a2e',   # 深蓝黑 → 墙
    PATH:  '#f0f0f0',   # 浅灰白 → 通路
    START: '#00e676',   # 亮绿   → 起点
    END:   '#ff1744',   # 红色   → 终点
    COIN:  '#ffd600',   # 金色   → 金币
    TRAP:  '#9c27b0',   # 紫色   → 陷阱
    BOSS:  '#ff6d00',   # 橙色   → BOSS
}

CURRENT_COLOR = '#00b0ff'   # 亮蓝 → 当前挖掘位置
VISITED_BG = '#e8e8e8'      # 已访问背景


def _grid_to_image(grid, current=None, ax=None, title=None):
    """将迷宫矩阵转为图像并绘制到 ax 上"""
    n = len(grid)
    img = np.ones((n, n, 3))

    for i in range(n):
        for j in range(n):
            val = grid[i][j]
            color_hex = COLORMAP.get(val, '#000000')
            r = int(color_hex[1:3], 16) / 255.0
            g = int(color_hex[3:5], 16) / 255.0
            b = int(color_hex[5:7], 16) / 255.0
            img[i, j] = [r, g, b]

    if current is not None:
        cx, cy = current
        if 0 <= cx < n and 0 <= cy < n:
            img[cx, cy] = [0.0, 0.69, 1.0]   # 亮蓝标记当前位置

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
    ax.clear()
    ax.imshow(img, interpolation='nearest')
    ax.set_xticks([])
    ax.set_yticks([])
    if title:
        ax.set_title(title, fontsize=14)
    return ax


def draw_maze(maze, current=None, title=None, save_path=None):
    """绘制迷宫静态图

    参数:
        maze: Maze 对象或 list[list[int]]
        current: 高亮坐标 (x, y)，可选
        title: 图片标题
        save_path: 保存路径（如 'maze.png'），不传则 plt.show()
    """
    grid = maze.maze if hasattr(maze, 'maze') else maze
    fig, ax = plt.subplots(figsize=(8, 8))
    _grid_to_image(grid, current=current, ax=ax, title=title)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
    else:
        plt.show()


def animate_generation(snapshots, output_path='maze_generation.gif',
                       interval=80, title='DFS 迷宫生成过程'):
    """将生成过程的快照列表制作为 GIF 动画

    参数:
        snapshots: list of (grid, current) 或 list of grid
        output_path: 输出文件路径
        interval: 帧间隔 (ms)
        title: 动画标题
    """
    if not snapshots:
        raise ValueError("snapshots 不能为空")

    fig, ax = plt.subplots(figsize=(8, 8))

    def update(frame):
        ax.clear()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(title, fontsize=14)

        data = snapshots[frame]
        if isinstance(data, tuple) and len(data) == 2:
            grid, current = data
        else:
            grid, current = data, None

        _grid_to_image(grid, current=current, ax=ax)

    ani = animation.FuncAnimation(fig, update, frames=len(snapshots),
                                   interval=interval, repeat=False)
    ani.save(output_path, writer='pillow', dpi=80)
    plt.close(fig)
    print(f"动画已保存至: {output_path} ({len(snapshots)} 帧)")


def capture_snapshots_from_generator(maze, generate_func, sample_rate=1):
    """运行生成器并采集快照

    返回: list of (grid_snapshot, current_position)
    """
    snapshots = []

    def on_step(m, cx, cy):
        if len(snapshots) % sample_rate == 0:
            grid_copy = [row[:] for row in m.maze]
            snapshots.append((grid_copy, (cx, cy)))

    generate_func(maze, on_step=on_step)
    final_grid = [row[:] for row in maze.maze]
    for _ in range(5):
        snapshots.append((final_grid, None))
    return snapshots


def draw_dp_path(maze, path_walk, title=None, save_path=None):
    """绘制 DP 最优资源收集路径

    参数:
        maze:     Maze 对象
        path_walk: collect_resources 返回的路径序列
        title:    图片标题
        save_path: 保存路径
    """
    grid = maze.maze
    n = len(grid)
    path_set = set(path_walk)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xticks([])
    ax.set_yticks([])

    # 画迷宫底色
    img = np.ones((n, n, 3))
    for i in range(n):
        for j in range(n):
            val = grid[i][j]
            color_hex = COLORMAP.get(val, '#000000')
            r = int(color_hex[1:3], 16) / 255.0
            g = int(color_hex[3:5], 16) / 255.0
            b = int(color_hex[5:7], 16) / 255.0
            img[i, j] = [r, g, b]

    ax.imshow(img, interpolation='nearest')

    # 在走过的路径上画半透明青色标记
    for x, y in path_set:
        if grid[x][y] not in {START, END}:
            rect = plt.Rectangle((y - 0.5, x - 0.5), 1, 1,
                                 facecolor='#00bcd4', alpha=0.4, linewidth=0)
            ax.add_patch(rect)

    # 画路径连线
    px, py = zip(*path_walk)
    ax.plot([y for y in py], [x for x in px], color='#ffeb3b',
            linewidth=2, alpha=0.8, zorder=3)

    if title:
        ax.set_title(title, fontsize=14)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
    else:
        plt.show()


def animate_dp_collection(snapshots, output_path='dp_collection.gif',
                          interval=100, title='DP Process'):
    if not snapshots:
        raise ValueError("snapshots empty")

    fig, ax = plt.subplots(figsize=(8, 8))

    def update(frame):
        ax.clear()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f'{title}  ({frame + 1}/{len(snapshots)})', fontsize=14)

        grid, walk_set, current = snapshots[frame]
        n = len(grid)
        img = np.ones((n, n, 3))

        for i in range(n):
            for j in range(n):
                val = grid[i][j]
                color_hex = COLORMAP.get(val, '#000000')
                r = int(color_hex[1:3], 16) / 255.0
                g = int(color_hex[3:5], 16) / 255.0
                b = int(color_hex[5:7], 16) / 255.0
                if (i, j) in walk_set and val in {PATH, START, END}:
                    img[i, j] = [0.0, 0.74, 0.83]
                else:
                    img[i, j] = [r, g, b]

        ax.imshow(img, interpolation='nearest')

        if current is not None:
            cx, cy = current
            if 0 <= cx < n and 0 <= cy < n:
                rect = plt.Rectangle((cy - 0.5, cx - 0.5), 1, 1,
                                     facecolor='#ffeb3b', alpha=0.9,
                                     linewidth=2, edgecolor='#ff6f00')
                ax.add_patch(rect)

    ani = animation.FuncAnimation(fig, update, frames=len(snapshots),
                                   interval=interval, repeat=True)
    ani.save(output_path, writer='pillow', dpi=80)
    plt.close(fig)
    print(f"DP : {output_path} ({len(snapshots)} )")
