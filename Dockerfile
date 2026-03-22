# Use a native ARM64 base image for Apple Silicon
FROM python:3.11-slim-bookworm

# 1. Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    rsync \
    zlib1g-dev \
    parallel \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Just (Command Runner)
RUN curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin

# 3. Install uv (Python Package Manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 4. Install Pythia 8
ENV PYTHIA_VERSION=8311
WORKDIR /opt
RUN curl -O https://pythia.org/download/pythia83/pythia${PYTHIA_VERSION}.tgz && \
    tar xvfz pythia${PYTHIA_VERSION}.tgz && \
    cd pythia${PYTHIA_VERSION} && \
    ./configure --with-python-config=python3-config --prefix=/usr/local && \
    # Using -j2 to prevent OOM (Out of Memory) on Docker Desktop
    make -j2 && \
    make install

# 5. Configure Environment Variables: for Pythia
ENV PYTHIA8DATA=/usr/local/share/Pythia8/xmldoc
ENV PYTHONPATH=/usr/local/lib:${PYTHONPATH:-}
ENV LD_LIBRARY_PATH=/usr/local/lib:${LD_LIBRARY_PATH:-}
# ADD THIS LINE TO FIX THE HARDLINK WARNING:
ENV UV_LINK_MODE=copy

WORKDIR /app

# 6. Initialize the Python environment
# We use --system-site-packages so 'uv' can see the Pythia bindings in /usr/local/lib
RUN uv venv .venv --system-site-packages
ENV PATH="/app/.venv/bin:$PATH"

# Default to bash
CMD ["/bin/bash"]
