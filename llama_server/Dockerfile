ARG CUDA_VERSION=13.3.0
ARG PORT=8081

FROM nvidia/cuda:${CUDA_VERSION}-devel-ubuntu22.04 AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    git cmake build-essential curl ca-certificates libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN git clone --recursive https://github.com/ggerganov/llama.cpp.git . \
    && git log -1 --format=%cd
RUN cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=120 -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_EXE_LINKER_FLAGS="-L/usr/local/cuda/lib64/stubs -lcuda" \
    -DCMAKE_SHARED_LINKER_FLAGS="-L/usr/local/cuda/lib64/stubs -lcuda" \
    && cmake --build build --config Release -j$(nproc) --target llama-server llama-cli
RUN test -f /src/build/bin/llama-server || (echo "BUILD FAILED - binary not found" && exit 1)


FROM nvidia/cuda:${CUDA_VERSION}-runtime-ubuntu22.04
ARG PORT

ENV DEBIAN_FRONTEND=noninteractive
ENV LD_LIBRARY_PATH=/src:$LD_LIBRARY_PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    ca-certificates \
    aria2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY --from=builder /src/build/bin/ /src/
WORKDIR /app

EXPOSE ${PORT}

CMD ["tail", "-f", "/dev/null"]
