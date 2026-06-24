# 迷宫设计项目 —— 主入口
# 用法: python main.py

import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))

from maze import Maze
from generators.backtrack_dfs import generate_maze_backtrack_dfs
from visualizer import (
    draw_maze, animate_generation, capture_snapshots_from_generator,
    draw_dp_path, animate_dp_collection
)
from dp_collector import collect_resources, collect_resources_snapshots
from boss_fight import boss_fight_branch_bound


def main():
    n = 15
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(output_dir, exist_ok=True)

    # ── 1. 迷宫生成 ─────────────────────────────────────
    print(f"[1/4] Generate {n}x{n} maze...")
    maze = Maze(n)
    snapshots = capture_snapshots_from_generator(maze, generate_maze_backtrack_dfs)
    animate_generation(snapshots, os.path.join(output_dir, 'backtrack_dfs.gif'),
                       interval=80, title=f'DFS {n}x{n}')
    draw_maze(maze, title=f'DFS {n}x{n}',
              save_path=os.path.join(output_dir, 'backtrack_dfs_final.png'))

    # ── 2. DP 资源收集 ──────────────────────────────────
    print(f"[2/4] DP resource collection...")
    max_gold, path_walk, dp_snaps = collect_resources_snapshots(maze)
    print(f"      Max gold = {max_gold}")

    animate_dp_collection(dp_snaps, os.path.join(output_dir, 'dp_collection.gif'),
                          interval=100, title=f'DP Value={max_gold}')
    draw_dp_path(maze, path_walk, title=f'DP Value={max_gold}',
                 save_path=os.path.join(output_dir, 'dp_optimal_path.png'))

    # ── 3. BOSS 战 ──────────────────────────────────────
    print(f"[3/4] BOSS fight (branch & bound)...")
    boss_hps = [60, 80]                     # 2 个 BOSS 血量
    skills = [(5, 0), (10, 2), (15, 4)]     # (伤害,冷却)
    max_limit = 25                          # 限定回合数
    coin_per_revive = 5                     # 每次复活消耗 5 金币

    bf = boss_fight_branch_bound(boss_hps, skills,
                                  max_rounds=max_limit,
                                  coin_per_revive=coin_per_revive)

    print(f"      Min rounds    = {bf['minRounds']}")
    print(f"      Skill seq     = {bf['sequence']}")
    print(f"      Coin/revive   = {bf['CoinConsumption']}")

    # 判断是否 GAME OVER
    if bf.get("resurrections_needed"):
        needed = bf["resurrections_needed"]
        total_cost = bf["total_coin_cost"]
        can_afford = max_gold >= total_cost
        bf["canAfford"] = can_afford
        bf["gameOver"] = not can_afford
        print(f"      Resurrections = {needed} (cost {total_cost} gold, have {max_gold})")
        print(f"      STATUS: {'Survive' if can_afford else 'GAME OVER'}")
    else:
        bf["gameOver"] = False
        bf["canAfford"] = True
        bf["resurrections_needed"] = 0
        bf["total_coin_cost"] = 0
        print(f"      STATUS: No resurrection needed")

    # ── 4. JSON 输出 ────────────────────────────────────
    print(f"[4/4] Exporting JSON...")
    output = {
        "maze": maze.to_json_matrix(),
        "B": boss_hps,
        "PlayerSkills": [list(s) for s in skills],
        "minRounds": bf["minRounds"],
        "CoinConsumption": bf["CoinConsumption"],
        "sequence": bf["sequence"],
        "maxRoundsLimit": max_limit,
        "resurrectionsNeeded": bf.get("resurrections_needed", 0),
        "totalCoinCost": bf.get("total_coin_cost", 0),
        "dpMaxGold": max_gold,
        "gameOver": bf.get("gameOver", False),
    }

    json_path = os.path.join(output_dir, 'result.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"      JSON -> {json_path}")
    print("Done!")


if __name__ == '__main__':
    main()
