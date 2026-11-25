import unittest
from fource_md import DeltaFragment, CUCVerificationGraph
from fource_md.deltas import (
    delta_01_reliability, delta_02_material_index, delta_03_mechanical_props,
    delta_04_tolerances, delta_05_stress_buckling, delta_06_failure_fatigue,
    delta_07_shaft_key, delta_08_journal_bearing, delta_09_rolling_bearing,
    delta_10_spur_gear, delta_11_helical_gear, delta_12_belt_chain,
    delta_13_brake_clutch, delta_14_helical_spring, delta_15_power_screw,
    delta_16_bolted_joint, delta_17_welds_adhesives, delta_18_axisymmetric
)


class TestFourceMDKernel(unittest.TestCase):
    def test_all_18_deltas_pass_nominal(self):
        fragments = [
            delta_01_reliability(),
            delta_02_material_index(),
            delta_03_mechanical_props(),
            delta_04_tolerances([0.05, 0.08, 0.04]),
            delta_05_stress_buckling(),
            delta_06_failure_fatigue(),
            delta_07_shaft_key(Ma_Nm=120.0, Tm_Nm=180.0, Se_MPa=280.0, Sut_MPa=850.0),
            delta_08_journal_bearing(),
            delta_09_rolling_bearing(C_kN=35.0, Fr_kN=2.2, Fa_kN=0.8, N_rpm=1450.0),
            delta_10_spur_gear(),
            delta_11_helical_gear(),
            delta_12_belt_chain(),
            delta_13_brake_clutch(),
            delta_14_helical_spring(),
            delta_15_power_screw(),
            delta_16_bolted_joint(),
            delta_17_welds_adhesives(),
            delta_18_axisymmetric(),
        ]
        self.assertEqual(len(fragments), 18)
        for frag in fragments:
            self.assertTrue(frag.passed, f"{frag.delta_id} failed nominal check: {frag.violations}")
            self.assertGreater(frag.persistence_margin, 0.0)

    def test_dag_invalidation_cascade(self):
        state = {"psi": 18.0}
        dag = CUCVerificationGraph()
        dag.register("Δ11", [], lambda _: delta_11_helical_gear(psi_deg=state["psi"]))
        dag.register("Δ16", ["Δ11"], lambda s: delta_16_bolted_joint(P_ext_N=s["Δ11"].outputs["Wa_N"] / 4.0))

        res1 = dag.run()
        hash1 = res1["Δ16"].state_hash

        state["psi"] = 30.0
        dag.invalidate("Δ11")
        res2 = dag.run()
        self.assertNotEqual(hash1, res2["Δ16"].state_hash)


if __name__ == "__main__":
    unittest.main()
