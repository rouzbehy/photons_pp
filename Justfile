set shell := ["bash", "-c"]

default:
    just --list

build-docker:
    sudo docker build -t photons_pythia . 

run-parallel:
    uv run python3 generate_jobs.py

    parallel --bar --colsep ' ' \
    "uv run python3 main.py --ptmin {1} --ptmax {2} --nevts {3} --ecm {4}" \
    :::: job_list.txt

aggregate:
    #!/usr/bin/bash
    for energy in 200 2760 5020
    do 
        uv run python3 consolidate.py --nevts 500000 --energy $energy
    done

clean:
    rm -f job_list.txt
    rm -rf .venv/

check-results:
    @echo "Checking for output files..."
    @find data -name "*.csv" | wc -l | xargs -I{} echo "Found {} of 77 expected files."
