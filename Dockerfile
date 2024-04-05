FROM python:3.11.9-slim

WORKDIR /

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        clang \
        git \
        wget \
        dos2unix \
    && rm -rf /var/lib/apt/lists/*

COPY scripts/ci/tools/linux/install_go.sh /install_go.sh
RUN chmod +x /install_go.sh && \
    dos2unix /install_go.sh && \
    /install_go.sh

COPY scripts/ci/tools/linux/install_zig.sh /install_zig.sh
RUN chmod +x /install_zig.sh && \
    dos2unix /install_zig.sh && \
    /install_zig.sh

RUN git clone https://github.com/agriyakhetarpal/hugo-python-distributions@main && \
    cd hugo-python-distributions && \
    python -m venv venv && \
    source venv/bin/activate && \
    pip install -e . && \
    pip install .

WORKDIR /hugo-python-distributions

CMD ["source", "venv/bin/activate"]
