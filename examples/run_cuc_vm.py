from fource_md.algebra import Phasor
from fource_md.vm import CUCInstruction, CUCVirtualMachine


def main():
    program = [
        CUCInstruction("LOAD", {"carriers": [
            Phasor(0.95, 0.12),
            Phasor(0.90, 0.24),
            Phasor(0.92, 0.18),
            Phasor(0.60, -2.40),
            Phasor(0.55, -2.10),
        ]}),
        CUCInstruction("COMPOSE", {"phasor": Phasor(1.05, 0.05), "beta": 1.5}),
        CUCInstruction("PROJECT", {"bounds": (0.1, 1.0)}),
        CUCInstruction("BRANCH", {"theta_ctr": 0.35}),
        CUCInstruction("STABILIZE", {"steps": 12, "kappa": 0.45}),
        CUCInstruction("SELECT"),
        CUCInstruction("HALT"),
    ]

    vm = CUCVirtualMachine()
    final_state = vm.run(program)

    print("=== CUC VIRTUAL MACHINE EXECUTION TRACE ===")
    for line in final_state.trace:
        print(" ", line)

    print("\n=== BASIN ENERGY SPECTRUM ===")
    for bname, sc in final_state.scores.items():
        print(f"  {bname}: r_lock={sc.C_phi_group:.4f} | C_total={sc.C_total:.4f} | E_total={sc.E_total:.4f}")

    assert final_state.selected_basin == "H1"
    print(f"\nHALTED ON OPTIMAL BASIN: {final_state.selected_basin}")


if __name__ == "__main__":
    main()
