from fource_md.algebra import Phasor
from fource_md.neural import CUCDeepNetwork


def main():
    # 2-Layer Deep CUC Network: 4 inputs -> 3 hidden basins -> 2 output classes
    net = CUCDeepNetwork([
        (4, ["Hidden_LowFreq", "Hidden_MidFreq", "Hidden_HighFreq"]),
        (3, ["Class_Stable", "Class_Unstable"]),
    ])

    samples = [
        ([Phasor(0.95, 0.10), Phasor(0.90, 0.15), Phasor(0.92, 0.12), Phasor(0.94, 0.08)], "Hidden_LowFreq", "Class_Stable"),
        ([Phasor(0.90, 2.20), Phasor(0.88, 2.35), Phasor(0.91, 2.10), Phasor(0.89, 2.25)], "Hidden_HighFreq", "Class_Unstable"),
    ]

    for epoch in range(1, 16):
        for x, h_target, y_target in samples:
            net.train_step(x, [h_target], y_target, lr=0.30)

    print("=== DEEP CUC NETWORK EVALUATION ===")
    for x, _, y_target in samples:
        pred, e_chain, scores = net.forward(x)
        print(f"Target: {y_target:15s} -> Pred: {pred:15s} | CS Chain Distortion E_chain = {e_chain:.4f}")
        assert pred == y_target, f"Expected {y_target}, got {pred}"

    print("\nSUCCESS: Multi-layer CUC neural network converged across hidden & output basins.")


if __name__ == "__main__":
    main()
