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

# 2. Install Just
RUN curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin

# 3. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 4. Install Pythia 8
ENV PYTHIA_VERSION=8311
WORKDIR /opt
RUN curl -O https://pythia.org/download/pythia83/pythia${PYTHIA_VERSION}.tgz && \
    tar xvfz pythia${PYTHIA_VERSION}.tgz && \
    cd pythia${PYTHIA_VERSION} && \
    ./configure --with-python-config=python3-config --prefix=/usr/local && \
    make -j2 && \
    make install

# 5. Environment Configuration
ENV PYTHIA8DATA=/usr/local/share/Pythia8/xmldoc
ENV PYTHONPATH=/usr/local/lib:${PYTHONPATH:-}
ENV LD_LIBRARY_PATH=/usr/local/lib:${LD_LIBRARY_PATH:-}
ENV UV_LINK_MODE=copy

# 6. User Setup
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g ${GROUP_ID} appuser && \
    useradd -l -u ${USER_ID} -g appuser -m appuser

# 7. Finalize Workspace
WORKDIR /app
RUN chown appuser:appuser /app
USER appuser

# Use system python directly to access Pythia bindings
CMD ["/bin/bash"]