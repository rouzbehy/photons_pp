import numpy as np
energies = [200, 2760, 5020]
num_bins = {200 : 10, 2760: 30, 5020: 40}
num_events = 50000
with open("job_list.txt", "w") as f:
    for ecm in energies:
        nbins = num_bins[ecm]
        pt_hats = np.logspace(np.log10(1.0), np.log10(ecm / 2.0), nbins)
        for i in range(len(pt_hats) - 1):
            low_bound = pt_hats[i]
            high_bound = pt_hats[i+1] if abs(pt_hats[i+1]-ecm/2.0)>1e-5 else 0
            f.write(f"{low_bound:.4f} {high_bound:.4f} {num_events} {ecm}\n")