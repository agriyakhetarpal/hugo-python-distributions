FROM python:3.11.9-slim

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
        musl-tools \
    && rm -rf /var/lib/apt/lists/*

ARG TARGETARCH=x86_64

RUN if [ "$TARGETARCH" = "arm64" ]; then \
        wget "https://ziglang.org/builds/zig-linux-aarch64-${ZIG_VERSION}.tar.xz" && \
        tar -C /usr/local -xf "zig-linux-aarch64-${ZIG_VERSION}.tar.xz" && \
        rm "zig-linux-aarch64-${ZIG_VERSION}.tar.xz"; \
    else \
        wget "https://ziglang.org/builds/zig-linux-x86_64-${ZIG_VERSION}.tar.xz" && \
        tar -C /usr/local -xf "zig-linux-x86_64-${ZIG_VERSION}.tar.xz" && \
        rm "zig-linux-x86_64-${ZIG_VERSION}.tar.xz"; \
    fi

ENV PATH="${PATH}:/usr/local/zig-linux-${TARGETARCH}-${ZIG_VERSION}"

RUN git clone https://github.com/agriyakhetarpal/hugo-python-distributions && \
    cd hugo-python-distributions && \
    pip install -e . && \
    pip install .

WORKDIR /hugo-python-distributions

CMD ["/bin/bash"]
