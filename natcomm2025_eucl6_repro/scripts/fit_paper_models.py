from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


KB_EV = 8.617333262145e-5
MU_B_EV_T = 5.7883818060e-5


def glum(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return 2 * (left - right) / (left + right)


def dp(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return 100 * (left - right) / (left + right)


def mpl(i_b: np.ndarray, i_0: np.ndarray) -> np.ndarray:
    return 100 * (i_b / i_0 - 1)


def demo(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    temp = np.linspace(80, 300, 150)
    alpha_ev_a = 0.152
    delta_e = 1.8e-3
    dp_model = 100 * np.tanh(delta_e / (2 * KB_EV * temp))

    field = np.linspace(-0.9, 0.9, 150)
    delta_bd = 11.7e-3
    delta_g = 2.0
    mpl_model = 100 * 0.03 * ((delta_g * MU_B_EV_T * field) ** 2) / (
        delta_bd**2 + (delta_g * MU_B_EV_T * field) ** 2
    )

    plt.figure()
    plt.plot(temp, dp_model)
    plt.xlabel("Temperature (K)")
    plt.ylabel("DP (%)")
    plt.title(f"DP toy model, alpha reported near {alpha_ev_a} eV A")
    plt.savefig(out / "dp_model_demo.png", dpi=300, bbox_inches="tight")
    plt.close()

    plt.figure()
    plt.plot(field, mpl_model)
    plt.xlabel("Magnetic field (T)")
    plt.ylabel("MPL (%)")
    plt.title(f"MPL toy model, Delta_B-D = {delta_bd * 1000:.1f} meV")
    plt.savefig(out / "mpl_model_demo.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("results/model_demo"))
    args = parser.parse_args()
    demo(args.out)
    print("Wrote model-demo figures. Use real extracted spectra to compute g_lum, DP, and MPL.")


if __name__ == "__main__":
    main()

