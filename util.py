import json


def get_ptbins():
    with open("settings.json") as fin:
        tmp = json.load(fin)
        ptbins_for_energy = {int(k): v for k, v in tmp.items()}
    return ptbins_for_energy
