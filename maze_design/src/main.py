# 迷宫设计项目 —— 主入口（4 算法对比）
# 用法: python main.py

import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))

from maze import Maze
from generators.backtrack_dfs import generate_maze_backtrack_dfs
from generators.divide_conquer import generate_maze_divide_conquer
from generators.greedy import generate_maze_greedy
from generators.branch_bound_bfs import generate_maze_branch_bound_bfs
from visualizer import (
    draw_maze, animate_generation, capture_snapshots_from_generator,
    draw_dp_path, animate_dp_collection
)
from dp_collector import collect_resources, collect_resources_snapshots
from boss_fight import boss_fight_branch_bound


ALGORITHMS = {
    "backtrack_dfs": ("DFS Backtracking", generate_maze_backtrack_dfs),
    "divide_conquer": ("Divide & Conquer", generate_maze_divide_conquer),
    "greedy": ("Greedy (Kruskal)", generate_maze_greedy),
    "branch_bound_bfs": ("Branch & Bound BFS", generate_maze_branch_bound_bfs),
}


def main():
    n = 15
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(output_dir, exist_ok=True)

    results = []

    for key, (label, gen_func) in ALGORITHMS.items():
        print(f"\n{'='*50}")
        print(f"  {label} ({key})")
        print(f"{'='*50}")

        maze = Maze(n)

        # ── 生成 + 动画 ──
        print(f"  Generating {n}x{n} maze...")
        snapshots = capture_snapshots_from_generator(maze, gen_func, sample_rate=1)
        gif_path = os.path.join(output_dir, f'{key}.gif')
        animate_generation(snapshots, gif_path, interval=80,
                           title=f'{label}  {n}x{n}')
        draw_maze(maze, title=f'{label} ({n}x{n})',
                  save_path=os.path.join(output_dir, f'{key}_final.png'))

        # ── DP 收集 ──
        print(f"  DP...")
        max_gold, path_walk, dp_snaps = collect_resources_snapshots(maze)
        print(f"    Max gold = {max_gold}")

        animate_dp_collection(dp_snaps,
                              os.path.join(output_dir, f'{key}_dp.gif'),
                              interval=100,
                              title=f'DP {label} value={max_gold}')
        draw_dp_path(maze, path_walk,
                     title=f'DP {label} value={max_gold}',
                     save_path=os.path.join(output_dir, f'{key}_dp.png'))

        # ── BOSS 战 ──
        boss_hps = [60, 80]
        skills = [(5, 0), (10, 2), (15, 4)]
        bf = boss_fight_branch_bound(boss_hps, skills,
                                      max_rounds=25, coin_per_revive=5)
        print(f"    Min rounds = {bf['minRounds']}")

        results.append({
            "algorithm": label,
            "key": key,
            "maze": maze.to_json_matrix(),
            "dpMaxGold": max_gold,
            "dpPathLength": len(path_walk),
            "bossMinRounds": bf["minRounds"],
            "bossSequence": bf["sequence"],
            "bossCoinPerRevive": bf["CoinConsumption"],
        })

    # ── 汇总 JSON ──
    compare = {
        "mazeSize": n,
        "bosses": [60, 80],
        "skills": [[5, 0], [10, 2], [15, 4]],
        "results": results,
    }
    json_path = os.path.join(output_dir, 'compare.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(compare, f, ensure_ascii=False, indent=2)

    print(f"\n  Compare JSON -> {json_path}")
    print("Done!")


if __name__ == '__main__':
    main()
