# BOSS 战 —— 分支限界策略优化
# 输入: 每个 BOSS 血量 + 玩家技能 [(伤害,冷却)]（至少一个 cd=0）
# 输出: 最少回合数、最优技能序列、复活所需金币数

def boss_fight_branch_bound(boss_hps, skills, max_rounds=None, coin_per_revive=5):
    """
    分支限界求击杀所有 BOSS 的最少回合数及最优技能序列。

    参数:
        boss_hps:       BOSS 血量列表 [h1, h2, ...]
        skills:         技能列表 [(dmg, cd), ...]，cd=0 为无冷却
        max_rounds:     限定回合数（可不传）
        coin_per_revive: 每次复活消耗金币（默认 5）

    返回:
        {
            "minRounds":        最少回合数,
            "sequence":         每回合使用的技能索引序列,
            "CoinConsumption":  每次复活消耗的金币,
        }
        若 max_rounds 指定 & minRounds > max_rounds:
            "resurrections_needed": 需复活次数,
            "total_coin_cost":      总金币消耗,
        }
    """
    n_skills = len(skills)
    n_bosses = len(boss_hps)
    if n_bosses == 0:
        return {"minRounds": 0, "sequence": [], "CoinConsumption": coin_per_revive}

    max_dmg = max(d[0] for d in skills)
    best = float('inf')
    best_seq = None

    # 下界：剩余血量 / 最大伤害（向上取整）
    def lower_bound(boss_idx, hp):
        rem = hp
        for k in range(boss_idx + 1, n_bosses):
            rem += boss_hps[k]
        return (rem + max_dmg - 1) // max_dmg

    def dfs(rounds, boss_idx, hp, cooldowns, seq):
        nonlocal best, best_seq

        if boss_idx >= n_bosses:
            if rounds < best:
                best = rounds
                best_seq = seq[:]
            return

        if rounds + lower_bound(boss_idx, hp) >= best:
            return

        for i, (dmg, cd) in enumerate(skills):
            if cooldowns[i] > 0:
                continue

            new_hp = hp - dmg
            new_cd = cooldowns[:]
            for j in range(n_skills):
                if new_cd[j] > 0:
                    new_cd[j] -= 1
            if cd > 0:
                new_cd[i] = cd

            seq.append(i)
            if new_hp <= 0:
                nxt = boss_idx + 1
                if nxt < n_bosses:
                    dfs(rounds + 1, nxt, boss_hps[nxt], new_cd, seq)
                elif rounds + 1 < best:
                    best = rounds + 1
                    best_seq = seq[:]
            else:
                dfs(rounds + 1, boss_idx, new_hp, new_cd, seq)
            seq.pop()

    dfs(0, 0, boss_hps[0], [0] * n_skills, [])

    result = {
        "minRounds": int(best),
        "sequence": best_seq if best_seq else [],
        "CoinConsumption": coin_per_revive,
    }

    if max_rounds is not None and best > max_rounds:
        result["resurrections_needed"] = (best + max_rounds - 1) // max_rounds
        result["total_coin_cost"] = result["resurrections_needed"] * coin_per_revive
        result["gameOver"] = False  # 待 DP 金币数量判定

    return result
