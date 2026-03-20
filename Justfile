set shell := ["bash", "-c"]

run-parallel:
    uv run python3 generate_jobs.py

    parallel --bar --colsep ' ' \
    "uv run python3 main.py --ptmin {1} --ptmax {2} --nevts {3} --ecm {4}" \
    :::: job_list.txt

clean:
    rm -f job_list.txt
    rm -rf .venv/

check-results:
    @echo "Checking for output files..."
    @find data -name "*.csv" | wc -l | xargs -I{} echo "Found {} of 57 expected files."
