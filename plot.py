import argparse
import tarfile
from pathlib import Path
from typing import Literal

import pandas as pd
from matplotlib import pyplot as plt
from numpy import pi as PI


def read_pp_200_spectrum(*, location: Path) -> pd.DataFrame:
    tar_name = "HEPData-ins1115828-v1-csv.tar.gz"
    # 2760: "HEPData-ins1664312-v1-csv.tar.gz"}
    file_name = "Figure10.csv"
    with tarfile.open(location / tar_name, "r") as fin:
        f = fin.extractfile(tar_name.replace(".tar.gz", "") + "/" + file_name)
        df = pd.read_csv(f, skiprows=27)

    columns = [
        "pT",
        "min_pT",
        "max_pT",
        "spec",
        "stat_pos",
        "stat_neg",
        "sys_pos",
        "sys_neg",
    ]
    df.columns = columns
    # df["spec"] = df["spec"]
    df["is_limit"] = False

    return df


def read_pp_2760_spectrum(*, location: Path) -> pd.DataFrame:
    tar_name = "HEPData-ins1664312-v1-csv.tar.gz"
    file_name = "Table9.csv"
    with tarfile.open(location / tar_name, "r") as fin:
        f = fin.extractfile(tar_name.replace(".tar.gz", "") + "/" + file_name)
        df = pd.read_csv(f, skiprows=12)

    df.columns = ["pT_range", "spec", "stat_pos", "stat_neg", "sys_pos", "sys_neg"]
    df["min_pT"] = df["pT_range"].str.extract("^(?P<min_PT>\d+\.\d+)\s-")
    df["max_pT"] = df["pT_range"].str.extract("^[^-]+-\s(?P<number>\d+\.\d+)$")
    df["spec"] = df["spec"]
    df["is_limit"] =df["spec"].astype(str).str.contains('90% CL') 
    df["spec"] = (
        df["spec"].astype(str).str.replace(r"\s*\(90% CL\)", "", regex=True).astype(float)
    )
    for item in ["min_pT", "max_pT", "spec"]:
        df[item] = df[item].astype(float)
    df["pT"] = 0.5 * (df["min_pT"] + df["max_pT"])
    df.drop(columns=["pT_range"], inplace=True)
    return df


SPECTYPE = Literal["invariant_yield", "invariant_cross_section"]
TOTAL_INELASTIC_CROSS_SECTION = {200: 43.82, 2760: 62.1}


def construct_my_spectrum(
    *, location: Path, energy: int, target_spectrum: SPECTYPE, eta_values: dict[str, float]
) -> pd.DataFrame:
    df = pd.read_csv(location / f"energy_{energy}.csv")

    if target_spectrum.lower() == "invariant_yield":
        cross_section_factor = TOTAL_INELASTIC_CROSS_SECTION[energy]
    else:
        cross_section_factor = 1.0

    scale_factor = 1e9 if energy == 200 else 1
    delta_eta = eta_values["eta_max"] - eta_values["eta_min"]
    delta_phi = 2 * PI

   
    df["x"] = 0.5 * (df["xmax"] + df["xmin"])
    df["dx"] = df["xmax"] - df["xmin"]

    df["spec"] = (
        scale_factor
        * df["y"]
        / (df["x"] * df["dx"] * delta_eta * delta_phi * cross_section_factor)
    )
    df["dspec"] = (
        scale_factor
        * df["dy"]
        / (df["x"] * df["dx"] * delta_eta * delta_phi * cross_section_factor)
    )

    
    df = df[["x", "dx", "spec", "dspec"]]
    return df


def plot(*, experiment: pd.DataFrame, theory: pd.DataFrame) -> plt.Figure:

    fig, axes = plt.subplots(nrows=2, ncols=1)
    ax = axes[0]

    non_limit = experiment[~experiment["is_limit"]]
    limits = experiment[experiment['is_limit']]
    ax.errorbar(
        limits['pT'], limits["spec"], 
        yerr=limits["spec"] * 0.3, # 30% length arrow
        uplims=True, 
        fmt='none', ecolor='red', label='90% CL Limit'
    )
    ax.scatter(non_limit["pT"], non_limit["spec"], color="red", label="Experiment")



    ax.plot(theory["x"], theory["spec"], color="black", label="theory")
    ax.fill_between(
        theory["x"],
        theory["spec"] - theory["dspec"],
        theory["spec"] + theory["dspec"],
        color="black",
        alpha=0.2,
    )

    ax.set_yscale("log")
    ax.legend(loc="best")

    plt.show()

    return fig


get_funcs = {200: read_pp_200_spectrum, 2760: read_pp_2760_spectrum}


parser = argparse.ArgumentParser("Plotter")
parser.add_argument("--energy", type=int, required=True, dest="energy")

if __name__ == "__main__":
    args = parser.parse_args()

    loc = Path("./experimental_data")

    target_spec = "invariant_yield" if args.energy == 2760 else "invariant_cross_section"

    experiment_df = get_funcs[args.energy](location=loc)
    theory_df = construct_my_spectrum(
        location=Path("./results"),
        energy=args.energy,
        target_spectrum=target_spec,
        eta_values={"eta_min": -1, "eta_max": 1},
    )

    fig = plot(theory=theory_df, experiment=experiment_df)
    fig.savefig(f"./fig_{args.energy}.pdf")
