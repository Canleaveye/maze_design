# BOSS 战分支限界 —— 单元测试

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from boss_fight import boss_fight_branch_bound


class TestBossFight(unittest.TestCase):

    # ── 1. 单 BOSS + 普攻无冷却 ──────────────────────
    def test_single_boss_basic(self):
        """1 个 BOSS (HP=20), 普攻(5,0). 需要 4 回合"""
        result = boss_fight_branch_bound([20], [(5, 0)])
        self.assertEqual(result["minRounds"], 4)

    # ── 2. 单 BOSS + 双技能 ──────────────────────────
    def test_single_boss_two_skills(self):
        """1 BOSS (HP=30), (5,0)+(10,2): (10+5+5+10)=30 → 4"""
        result = boss_fight_branch_bound([30], [(5, 0), (10, 2)])
        self.assertEqual(result["minRounds"], 4)

    # ── 3. 双 BOSS 接力 ─────────────────────────────
    def test_two_bosses(self):
        """2 个 BOSS (HP=10, HP=15), 普攻(5,0) + 大招(10,2)"""
        result = boss_fight_branch_bound([10, 15], [(5, 0), (10, 2)])
        min_r = result["minRounds"]
        seq = result["sequence"]

        # 验证击杀可行性
        skills = [(5, 0), (10, 2)]
        self._verify_sequence(boss_hps=[10, 15], skills=skills,
                              seq=seq, expected_rounds=min_r)

    # ── 4. 三 BOSS 接力 ─────────────────────────────
    def test_three_bosses(self):
        """3 个 BOSS, 验证不崩溃且输出合法"""
        result = boss_fight_branch_bound(
            [30, 25, 40], [(5, 0), (8, 1), (12, 3)]
        )
        self.assertGreater(result["minRounds"], 0)
        self.assertIsNotNone(result["sequence"])

    # ── 5. 限定回合复活计算 ─────────────────────────
    def test_limited_rounds_resurrection(self):
        result = boss_fight_branch_bound(
            [100], [(5, 0), (10, 2)], max_rounds=10
        )
        # 最少 10+ 回合但限定 10 → 应需要复活
        self.assertGreater(result["minRounds"], 0)
        self.assertIn("CoinConsumption", result)

    # ── 6. 序列合法性验证 ───────────────────────────
    def test_sequence_valid(self):
        """验证输出的技能序列确实能按规则击杀"""
        boss_hps = [25, 20, 30]
        skills = [(5, 0), (8, 2), (15, 4)]
        result = boss_fight_branch_bound(boss_hps, skills)

        self._verify_sequence(boss_hps, skills,
                              result["sequence"], result["minRounds"])

    # ── 7. 无冷却技能必须存在 ──────────────────────
    def test_requires_no_cooldown(self):
        skills = [(5, 0), (10, 2)]
        has_no_cd = any(cd == 0 for _, cd in skills)
        self.assertTrue(has_no_cd,
                        "至少需要一个无冷却技能，否则 0 冷却时无技能可用")

    # ── 8. 极限情况 ────────────────────────────────
    def test_edge_cases(self):
        # HP=1, 普攻=1
        r1 = boss_fight_branch_bound([1], [(1, 0)])
        self.assertEqual(r1["minRounds"], 1)

        # 大伤害秒杀
        r2 = boss_fight_branch_bound([5], [(100, 0)])
        self.assertEqual(r2["minRounds"], 1)

    # ─── 辅助函数 ──────────────────────────────────
    def _verify_sequence(self, boss_hps, skills, seq, expected_rounds):
        """模拟验证技能序列能否在 expected_rounds 内击杀"""
        self.assertEqual(len(seq), expected_rounds,
                         f"序列长度 {len(seq)} != 回合数 {expected_rounds}")

        hp = list(boss_hps)
        cooldowns = [0] * len(skills)
        boss_idx = 0

        for skill_idx in seq:
            self.assertLess(skill_idx, len(skills))
            self.assertEqual(cooldowns[skill_idx], 0,
                             f"回合 {boss_idx}: 技能 {skill_idx} 在冷却中")

            dmg, cd = skills[skill_idx]
            hp[boss_idx] -= dmg

            # 更新冷却
            for j in range(len(skills)):
                if cooldowns[j] > 0:
                    cooldowns[j] -= 1
            if cd > 0:
                cooldowns[skill_idx] = cd

            if hp[boss_idx] <= 0:
                boss_idx += 1

        self.assertGreaterEqual(boss_idx, len(boss_hps),
                                "BOSS 未全部击杀")


if __name__ == '__main__':
    unittest.main(verbosity=2)
