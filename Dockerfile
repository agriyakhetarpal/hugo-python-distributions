FROM python:3.11.9-slim

ENV GO_VERSION=1.22.2
ENV ZIG_VERSION=0.11.0

WORKDIR /

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        clang \
        git \
        wget \
        dos2unix \
        xz-utils \
    && rm -rf /var/lib/apt/lists/*

RUN wget "https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz" && \
    tar -C /usr/local -xzf "go${GO_VERSION}.linux-amd64.tar.gz" && \
    rm "go${GO_VERSION}.linux-amd64.tar.gz"

ENV PATH="${PATH}:/usr/local/go/bin"

RUN wget "https://ziglang.org/builds/zig-linux-x86_64-${ZIG_VERSION}.tar.xz" && \
    tar -C /usr/local -xf "zig-linux-x86_64-${ZIG_VERSION}.tar.xz" && \
    rm "zig-linux-x86_64-${ZIG_VERSION}.tar.xz"

ENV PATH="${PATH}:/usr/local/zig-linux-x86_64-${ZIG_VERSION}"

RUN git clone https://github.com/agriyakhetarpal/hugo-python-distributions && \
    cd hugo-python-distributions && \
    pip install -e . && \
    pip install .

WORKDIR /hugo-python-distributions

CMD ["/bin/bash"]
