from __future__ import annotations

import argparse
import csv
import itertools
import math
from pathlib import Path

import numpy as np
from pymatgen.core import Structure


def angle(v1: np.ndarray, v2: np.ndarray) -> float:
    c = float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    c = max(-1.0, min(1.0, c))
    return math.degrees(math.acos(c))


def analyze(structure: Structure) -> list[dict[str, float | int]]:
    rows = []
    eu_indices = [i for i, site in enumerate(structure) if site.specie.symbol == "Eu"]
    for eu_i in eu_indices:
        eu = structure[eu_i]
        cl_neighbors = []
        for j, site in enumerate(structure):
            if site.specie.symbol != "Cl":
                continue
            dist, image = structure.lattice.get_distance_and_image(eu.frac_coords, site.frac_coords)
            cart = structure.lattice.get_cartesian_coords(site.frac_coords + image - eu.frac_coords)
            cl_neighbors.append((j, dist, cart))
        cl_neighbors.sort(key=lambda x: x[1])
        nearest = cl_neighbors[:6]
        if len(nearest) < 6:
            continue
        dists = np.array([x[1] for x in nearest], dtype=float)
        vecs = [x[2] for x in nearest]
        pair_angles = []
        for a, b in itertools.combinations(vecs, 2):
            pair_angles.append(angle(a, b))
        pair_angles = np.array(pair_angles)
        cis = np.sort(pair_angles)[:12]
        trans = np.sort(pair_angles)[-3:]
        d_mean = float(np.mean(dists))
        bond_distortion = float(np.mean(((dists - d_mean) / d_mean) ** 2))
        cis_dev = float(np.mean(np.abs(cis - 90.0)))
        trans_dev = float(np.mean(np.abs(trans - 180.0)))
        rows.append(
            {
                "eu_index": eu_i,
                "eu_cl_mean_A": d_mean,
                "eu_cl_min_A": float(np.min(dists)),
                "eu_cl_max_A": float(np.max(dists)),
                "eu_cl_range_A": float(np.max(dists) - np.min(dists)),
                "bond_length_distortion": bond_distortion,
                "cis_angle_mean_deg": float(np.mean(cis)),
                "cis_angle_abs_dev_from_90_deg": cis_dev,
                "trans_angle_mean_deg": float(np.mean(trans)),
                "trans_angle_abs_dev_from_180_deg": trans_dev,
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structure", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    structure = Structure.from_file(args.structure)
    rows = analyze(structure)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["eu_index"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {args.out} with {len(rows)} Eu sites")


if __name__ == "__main__":
    main()

