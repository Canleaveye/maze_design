# 迷宫设计项目 —— 主入口
# 用法: python main.py

import os
import sys

# 确保 src 目录在路径中
sys.path.insert(0, os.path.dirname(__file__))

from maze import Maze
from generators.backtrack_dfs import generate_maze_backtrack_dfs
from visualizer import draw_maze, animate_generation, capture_snapshots_from_generator


def main():
    n = 15
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(output_dir, exist_ok=True)

    print(f"  生成 {n}x{n} 迷宫（回溯/DFS）...")
    maze = Maze(n)

    # —— 1. 采集生成过程快照 ——————————————————————————
    snapshots = capture_snapshots_from_generator(
        maze, generate_maze_backtrack_dfs, sample_rate=1
    )

    # —— 2. 导出动画 GIF ——————————————————————————————
    gif_path = os.path.join(output_dir, 'backtrack_dfs.gif')
    animate_generation(snapshots, gif_path, interval=80,
                       title=f'DFS 回溯迷宫生成 ({n}x{n})')

    # —— 3. 导出最终迷宫静态图 —————————————————————————
    png_path = os.path.join(output_dir, 'backtrack_dfs_final.png')
    draw_maze(maze, title=f'DFS 回溯迷宫 ({n}x{n})', save_path=png_path)

    print(f"  最终迷宫已保存至: {png_path}")
    print("  完成!")


if __name__ == '__main__':
    main()
