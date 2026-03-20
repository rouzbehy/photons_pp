# Pythia Photons

Simple python-based program for generating photon spectra for proton-proton collisions. Target centre-of-mass energies are $200$, $2760$ and $5020$ GeV for a series of $\hat{p}_T$ bins. 

The program uses `Just` for task runs and `Docker` for replicability.

The project is managed by `uv` and needs `just` and `docker` to have been installed on the system

## Help
1. To build the docker container, run 
`docker build -t photons_pythia . `
2. To run the docker container in interactive mode, run `docker run -it --rm -v $(pwd):/app photons_pythia /bin/bash`.
Note that the `-v $(pwd):/app` is needed to make the directory accessible from outside of the container and make its data persistent after the simulations are done.