set shell := ["bash", "-c"]

default:
    @just --list

build-docker:
    sudo docker build -t photons_pythia . 

run-parallel energy num_events:
    uv run python3 generate_jobs.py --ecm {{energy}} --nevts {{num_events}}

    parallel --bar --colsep ' ' \
    "uv run python3 main.py --ptmin {1} --ptmax {2} --nevts {3} --ecm {4}" \
    :::: job_list.txt

aggregate:
    #!/usr/bin/bash
    # Ensure the file exists before attempting to read
    [ -f metadata.txt ] || { echo "metadata.txt not found"; exit 1; }
    
    while read -r e n || [ -n "$e" ]; do
        uv run python3 consolidate.py --energy "$e" --nevts "$n"
    done < metadata.txt

plot energy:
    uv run plot.py --energy {{energy}}

clean:
    rm -f job_list.txt
    rm -rf .venv/

check-results:
    @echo "Checking for output files..."
    @find data -name "*.csv" | wc -l | xargs -I{} echo "Found {} files."
