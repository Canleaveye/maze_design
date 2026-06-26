# 迷宫设计项目 —— 主入口（4 算法对比 + 复杂度分析）
# 用法: python main.py

import os
import sys
import json
import time

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
from utils import analyze_maze


ALGORITHMS = {
    "backtrack_dfs": ("DFS Backtracking", generate_maze_backtrack_dfs),
    "divide_conquer": ("Divide & Conquer", generate_maze_divide_conquer),
    "greedy": ("Greedy (Kruskal)", generate_maze_greedy),
    "branch_bound_bfs": ("Branch & Bound BFS", generate_maze_branch_bound_bfs),
}

# 理论复杂度参考
COMPLEXITY = {
    "backtrack_dfs":  {"time": "O(V+E)", "space": "O(V)",   "desc": "DFS 一次遍历所有房间"},
    "divide_conquer": {"time": "O(V log V)", "space": "O(log V)", "desc": "递归二分为 logV 层"},
    "greedy":         {"time": "O(E log E)", "space": "O(V)", "desc": "并查集 + 洗牌 E 条边"},
    "branch_bound_bfs":{"time": "O(V+E)", "space": "O(V)",   "desc": "BFS 队列扩展所有房间"},
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

        # ── 计时（无可视化）─────────────────────────────
        maze_tmp = Maze(n)
        t0 = time.perf_counter()
        gen_func(maze_tmp)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        # ── 分析指标 ────────────────────────────────────
        analysis = analyze_maze(maze_tmp)

        # ── 重新生成（带可视化）─────────────────────────
        maze = Maze(n)
        print(f"  Generating {n}x{n} maze...")
        snapshots = capture_snapshots_from_generator(maze, gen_func, sample_rate=1)
        anim_path = os.path.join(output_dir, f'{key}.gif')
        animate_generation(snapshots, anim_path, interval=80,
                           title=f'{label} {n}x{n}')
        draw_maze(maze, title=f'{label} ({n}x{n})',
                  save_path=os.path.join(output_dir, f'{key}_final.png'))

        # ── DP 收集 ────────────────────────────────────
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

        # ── BOSS 战（1 个标志物，内含 4 个 BOSS 群）───
        boss_hps = [30, 40, 50, 60]           # 4 个 BOSS，总 HP=180
        skills = [(5, 0), (10, 2), (15, 4)]
        bf = boss_fight_branch_bound(boss_hps, skills,
                                      max_rounds=25, coin_per_revive=5)
        print(f"    Min rounds = {bf['minRounds']}")

        # 打印复杂度
        complex_info = COMPLEXITY[key]
        print(f"    Time = {elapsed_ms:.2f} ms  ({complex_info['time']}, {complex_info['desc']})")
        print(f"    Dead ends = {analysis['deadEnds']}, Branching = {analysis['avgBranching']}")
        print(f"    Path len = {analysis['pathLength']}, Max depth = {analysis['maxDepth']}")

        results.append({
            "algorithm": label,
            "key": key,
            "maze": maze.to_json_matrix(),
            "complexity": {
                "timeTheoretical": complex_info["time"],
                "spaceTheoretical": complex_info["space"],
                "timeMs": round(elapsed_ms, 2),
                "description": complex_info["desc"],
            },
            "analysis": analysis,
            "dpMaxGold": max_gold,
            "dpPathLength": len(path_walk),
            "bossMinRounds": bf["minRounds"],
            "bossSequence": bf["sequence"],
            "bossCoinPerRevive": bf["CoinConsumption"],
        })

    # ── 汇总 ──
    compare = {
        "mazeSize": n,
        "bosses": [30, 40, 50, 60],
        "skills": [[5, 0], [10, 2], [15, 4]],
        "complexitySummary": {
            k: {"time": COMPLEXITY[k]["time"], "space": COMPLEXITY[k]["space"]}
            for k in COMPLEXITY
        },
        "results": results,
    }
    json_path = os.path.join(output_dir, 'compare.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(compare, f, ensure_ascii=False, indent=2)

    # ── 打印对比表 ──
    print(f"\n{'='*70}")
    print(f"  Complexity & Challenge Comparison (n={n})")
    print(f"{'='*70}")
    print(f"  {'Algorithm':<20} {'Time (ms)':>10} {'DeadEnds':>10} {'Branch':>8} {'Path':>6} {'DP Gold':>9}")
    print(f"  {'-'*63}")
    for r in results:
        a = r["analysis"]
        print(f"  {r['algorithm']:<20} {r['complexity']['timeMs']:>9.2f}  {a['deadEnds']:>9}  {a['avgBranching']:>7}  {a['pathLength']:>5}  {r['dpMaxGold']:>8}")
    print(f"\n  Compare JSON -> {json_path}")
    print("Done!")


if __name__ == '__main__':
    main()
