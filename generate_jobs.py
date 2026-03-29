import argparse
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(prog="Run metadata and job generator")
parser.add_argument("--ecm", type=float, default=200, help="Centre of mass energy value")
parser.add_argument("--nevts", type=int, default=2000, help="Number of events")

num_bins = {200: 20, 2760: 30, 5020: 40}

PWD = Path.cwd()


def main():
    args = parser.parse_args()
    ecm = args.ecm
    num_events = args.nevts
    with open(f"{PWD}/job_list.txt", "w") as f:
        nbins = num_bins[ecm]
        pt_hats = np.logspace(np.log10(1.0), np.log10(ecm / 2.0), nbins)
        for i in range(len(pt_hats) - 1):
            low_bound = pt_hats[i]
            high_bound = pt_hats[i + 1] if abs(pt_hats[i + 1] - ecm / 2.0) > 1e-5 else 0
            f.write(f"{low_bound:.4f} {high_bound:.4f} {num_events} {ecm}\n")
    with open(f"{PWD}/metadata.txt", "w") as f:
        f.write(f"{int(ecm)} {int(num_events)}")


if __name__ == "__main__":
    main()
