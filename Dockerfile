FROM python:3.11.9-slim

WORKDIR /

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        clang \
        git \
        wget \
        dos2unix \
        xz-utils \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://golang.org/dl/go1.22.1.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.22.1.linux-amd64.tar.gz && \
    rm go1.22.1.linux-amd64.tar.gz

ENV PATH="${PATH}:/usr/local/go/bin"

RUN wget https://ziglang.org/builds/zig-linux-x86_64-0.11.0.tar.xz && \
    tar -C /usr/local -xf zig-linux-x86_64-0.11.0.tar.xz && \
    rm zig-linux-x86_64-0.11.0.tar.xz

ENV PATH="${PATH}:/usr/local/zig-linux-x86_64-0.11.0"

RUN git clone https://github.com/agriyakhetarpal/hugo-python-distributions && \
    cd hugo-python-distributions && \
    python -m venv venv && \
    /hugo-python-distributions/venv/bin/python -m pip install -e . && \
    /hugo-python-distributions/venv/bin/python -m pip install .

WORKDIR /hugo-python-distributions

CMD ["/hugo-python-distributions/venv/bin/python", "-m", "venv/bin/activate"]
