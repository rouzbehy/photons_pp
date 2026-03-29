import argparse
import re
from dataclasses import dataclass
from glob import glob
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(prog="Spectra-Consolidation")
parser.add_argument("--energy", required=True, type=int, dest="energy")
parser.add_argument("--nevts", required=True, type=int, dest="nevts")


@dataclass(kw_only=True, slots=True, frozen=True)
class Spectrum:
    """Assumption is that the spectrum is already scaled by the cross section"""

    com: int
    min_x_values: np.ndarray
    max_x_values: np.ndarray
    y_values: np.ndarray
    dy_values: np.ndarray


def build_total_spectrum(*, master_directory: Path, energy: int, nevts: int) -> Spectrum:
    cross_section_files = glob(str(master_directory) + f"/energy_{energy}/pt_hat_*.txt")
    spectra_files = glob(str(master_directory) + f"/energy_{energy}/pt_hat_*.csv")
    spectra: list[Spectrum] = []
    for spectrum_file in spectra_files:
        csec_index = cross_section_files.index(spectrum_file.replace("csv", "txt"))
        csec_file = cross_section_files[csec_index]

        (xmin, xmax, y) = np.loadtxt(spectrum_file, skiprows=1, unpack=True, delimiter=",")
        with open(csec_file, "r") as fin:
            content = fin.readlines()
            m = re.findall(
                r"(?is)^Generated Cross-section: (?P<cross_section>\d+\.\d+e(?:-|\+|)\d+)\smb(?:\n|)$",
                content[0],
            )
            cross_section = float(m[0])
        spectra.append(
            Spectrum(
                com=energy,
                min_x_values=xmin,
                max_x_values=xmax,
                y_values=y * cross_section / nevts,
                dy_values=np.sqrt(y) * cross_section / nevts,
            )
        )

    spec = spectra[0]
    for s in spectra[1:]:
        spec = combine(spec, s)
    return spec


def combine(a: Spectrum, b: Spectrum) -> Spectrum:
    if not isinstance(b, Spectrum):
        raise NotImplementedError

    assert a.com == b.com
    # Standard element-wise addition with numpy
    y = a.y_values + b.y_values
    # Quadrature sum for errors
    dy = np.sqrt(a.dy_values**2 + b.dy_values**2)

    return Spectrum(
        com=a.com,
        min_x_values=a.min_x_values,
        max_x_values=a.max_x_values,
        y_values=y,
        dy_values=dy,
    )


def write_to_file(*, spec: Spectrum, file_name_and_path: str) -> None:
    fname = Path(file_name_and_path)
    with open(fname, "w") as fout:
        fout.write("xmin,xmax,y,dy\n")
        for low, high, y, dy in zip(
            spec.min_x_values, spec.max_x_values, spec.y_values, spec.dy_values
        ):
            fout.write(f"{low:0.3f},{high:0.3f},{y:0.4e},{dy:0.4e}\n")


if __name__ == "__main__":
    args = parser.parse_args()
    raw_dir = Path("./data/")

    s = build_total_spectrum(master_directory=raw_dir, energy=args.energy, nevts=args.nevts)
    write_to_file(spec=s, file_name_and_path=f"./results/energy_{args.energy}.csv")
