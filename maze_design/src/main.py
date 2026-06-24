# 迷宫设计项目 —— 主入口
# 用法: python main.py

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from maze import Maze
from generators.backtrack_dfs import generate_maze_backtrack_dfs
from visualizer import (
    draw_maze, animate_generation, capture_snapshots_from_generator,
    draw_dp_path, animate_dp_collection
)
from dp_collector import collect_resources, collect_resources_snapshots


def main():
    n = 15
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(output_dir, exist_ok=True)

    print(f"[1/3] Generate {n}x{n} maze (backtrack/DFS)...")
    maze = Maze(n)

    snapshots = capture_snapshots_from_generator(
        maze, generate_maze_backtrack_dfs, sample_rate=1
    )

    gif_path = os.path.join(output_dir, 'backtrack_dfs.gif')
    animate_generation(snapshots, gif_path, interval=80,
                       title=f'DFS {n}x{n}')

    png_path = os.path.join(output_dir, 'backtrack_dfs_final.png')
    draw_maze(maze, title=f'DFS {n}x{n}', save_path=png_path)

    # ── Task 2: DP resource collection ──────────────────────
    print(f"[2/3] DP resource collection...")
    max_value, path_walk, dp_snapshots = collect_resources_snapshots(maze, sample_rate=1)

    print(f"  Optimal value = {max_value}")
    print(f"  Path length   = {len(path_walk)} steps, {len(dp_snapshots)} frames")

    # DP process animation
    dp_gif = os.path.join(output_dir, 'dp_collection.gif')
    animate_dp_collection(dp_snapshots, dp_gif, interval=100,
                          title=f'DP   ={max_value}')

    # Final DP path image
    dp_png = os.path.join(output_dir, 'dp_optimal_path.png')
    draw_dp_path(maze, path_walk,
                 title=f'DP   ={max_value} ({len(path_walk)} )',
                 save_path=dp_png)

    print(f"[3/3] Done! Output in: {output_dir}")


if __name__ == '__main__':
    main()
