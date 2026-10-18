# OpenFOAM 13 (openfoam.org, apt) in a container, for running the CFD pipelines on a shared server without
# installing anything on the host. The run scripts source /opt/openfoam13/etc/bashrc, as in the original runs.
# Build: docker build -t sbd-openfoam13 cfd/docker
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates wget gnupg software-properties-common \
      python3-numpy python3-scipy python3-matplotlib python3-yaml xz-utils git \
 && wget -qO /etc/apt/trusted.gpg.d/openfoam.asc https://dl.openfoam.org/gpg.key \
 && add-apt-repository -y http://dl.openfoam.org/ubuntu \
 && apt-get update && apt-get install -y --no-install-recommends openfoam13 \
 && rm -rf /var/lib/apt/lists/*
