import math
import unittest
from fource_md import (
    CUCVerificationGraph,
    Phasor,
    UnifiedCoherenceScore,
    branch_contradictions,
    coa_star,
    evaluate_hypothesis_branches,
    fuse_group,
    kuramoto_order,
)
from fource_md.deltas import (
    delta_01_reliability, delta_02_material_index, delta_03_mechanical_props,
    delta_04_tolerances, delta_05_stress_buckling, delta_06_failure_fatigue,
    delta_07_shaft_key, delta_08_journal_bearing, delta_09_rolling_bearing,
    delta_10_spur_gear, delta_11_helical_gear, delta_12_belt_chain,
    delta_13_brake_clutch, delta_14_helical_spring, delta_15_power_screw,
    delta_16_bolted_joint, delta_17_welds_adhesives, delta_18_axisymmetric,
)


class TestRefactoredFourceKernel(unittest.TestCase):
    def test_pfa_order_invariance(self):
        z1 = Phasor(2.0, 0.0)
        z2 = Phasor(3.0, math.pi / 3.0)
        z3 = Phasor(1.5, math.pi / 2.0)
        fused_abc, r_abc = fuse_group([z1, z2, z3], beta=2.0)
        fused_cba, r_cba = fuse_group([z3, z2, z1], beta=2.0)
        self.assertAlmostEqual(r_abc, r_cba, places=8)
        self.assertAlmostEqual(fused_abc.A, fused_cba.A, places=8)

    def test_contradiction_branching_and_cs_selection(self):
        items = ["e1", "e2", "e3", "e4"]
        scores = {("e1", "e2"): 0.1, ("e1", "e3"): 0.8, ("e2", "e3"): 0.7, ("e3", "e4"): 0.2}
        def ctr(a, b):
            return scores.get((a, b), scores.get((b, a), 0.1))
        clusters = branch_contradictions(items, ctr, theta_ctr=0.6)
        self.assertEqual(clusters, [["e1", "e2"], ["e3", "e4"]])

    def test_coa_star_box_projection(self):
        res = coa_star(8.0, 5.0, lambda a, b: a + b, lambda x: max(0.0, min(10.0, x)))
        self.assertEqual(res, 10.0)

    def test_all_18_chapters_nominal_pass(self):
        frags = [
            delta_01_reliability(), delta_02_material_index(), delta_03_mechanical_props(),
            delta_04_tolerances([0.05, 0.08, 0.04]), delta_05_stress_buckling(), delta_06_failure_fatigue(),
            delta_07_shaft_key(), delta_08_journal_bearing(), delta_09_rolling_bearing(),
            delta_10_spur_gear(), delta_11_helical_gear(), delta_12_belt_chain(),
            delta_13_brake_clutch(), delta_14_helical_spring(), delta_15_power_screw(),
            delta_16_bolted_joint(), delta_17_welds_adhesives(), delta_18_axisymmetric(),
        ]
        self.assertEqual(len(frags), 18)
        for f in frags:
            self.assertTrue(f.passed, f"{f.delta_id} failed: {f.violations}")
            self.assertGreaterEqual(f.E_total, 0.0)

    def test_dag_branching_and_invalidation(self):
        g_worm = CUCVerificationGraph()
        g_worm.register("Δ15", [], lambda _: delta_15_power_screw())

        g_helical = CUCVerificationGraph()
        g_helical.register("Δ11", [], lambda _: delta_11_helical_gear(psi_deg=18.0))
        g_helical.register("Δ16", ["Δ11"], lambda s: delta_16_bolted_joint(P_ext_N=s["Δ11"].outputs["Wa_N"]))

        winner, min_e, _ = evaluate_hypothesis_branches({"Worm": g_worm, "Helical": g_helical})
        self.assertIn(winner, {"Worm", "Helical"})
        self.assertGreater(min_e, 0.0)


if __name__ == "__main__":
    unittest.main()
