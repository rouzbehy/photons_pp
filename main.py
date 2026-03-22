import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

import pythia8

from histogram import Histogram

PartonType: TypeAlias = pythia8.Particle


@dataclass(kw_only=True)
class KinematicCuts:
    lower_eta: float
    upper_eta: float


def capture(p: PartonType, cuts: KinematicCuts) -> bool:
    if cuts.lower_eta < p.eta() < cuts.upper_eta:
        return True
    return False


parser = argparse.ArgumentParser(prog="Photon Spectrum Generator")
parser.add_argument("--ptmin", type=float, default=10, help="Minimum pTHat value")
parser.add_argument("--ptmax", type=float, default=0, help="Maximum pTHat value")
parser.add_argument("--ecm", type=float, default=2760, help="Centre of mass energy value")
parser.add_argument("--nevts", type=int, default=2000, help="Number of events")


if __name__ == "__main__":
    args = parser.parse_args()
    # Initialize Pythia
    pythia = pythia8.Pythia()
    pythia.readString("HardQCD:all = on")  # Generic QCD process
    pythia.readString(
        "HadronLevel:all=off"
    )  # Do not hadronize or do any hadron level activity
    pythia.readString("PromptPhoton:all=on")  # want all prompt photons
    pythia.readString(
        f"PhaseSpace:pTHatMin={args.ptmin}"
    )  # phase space cuts in the hard process
    pythia.readString(
        f"PhaseSpace:pTHatMax={args.ptmax}"
    )  # phase space cuts in the hard process
    pythia.readString(f"Beams:eCM={args.ecm}")  # beam center of mass energy
    pythia.readString("PDF:pSet=8")  # CTEQ6L.1
    pythia.readString("Print:quiet=on")
    pythia.readString("Print:next=off")

    pythia.init()

    cuts = KinematicCuts(lower_eta=-1.0, upper_eta=1.0)
    hist = Histogram(bins=10, range_min=1, range_max=50, scale="log")

    for i in range(args.nevts):
        if not pythia.next():
            continue
        # Count photons (ID == 22) in the event record
        target_photons_in_event = filter(
            lambda x: capture(x, cuts), [p for p in pythia.event if p.id() == 22]
        )
        # bin the photons that passed the filter
        for p in target_photons_in_event:
            hist.add(p.pT())

    # write hist to file
    directory = Path(f"./data/energy_{int(args.ecm)}/")
    directory.mkdir(exist_ok=True, parents=True)
    fname = f"pt_hat_{args.ptmin:0.2f}_{args.ptmax:0.2f}".replace(".", "p") + ".csv"
    fname_and_path = directory / fname
    with open(fname_and_path, "w") as fout:
        fout.write("ptmin,ptmax,count\n")
        bins, values = hist.bins_range(), hist.data()
        for i in range(len(bins)):
            fout.write(f"{bins[i][0]:0.2f},{bins[i][1]:0.2f},{values[i]:0.2f}\n")

    fname_and_path = Path(str(fname_and_path).replace(".csv", ".txt"))
    with open(fname_and_path, "w") as fout:
        # Retrieve Results
        sigma = pythia.infoPython().sigmaGen()  # Cross-section in mb
        error = pythia.infoPython().sigmaErr()  # Error in mb

        fout.write(f"Generated Cross-section: {sigma:.4e} mb\n")
        fout.write(f"Error: {error:.4e} mb")
