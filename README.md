# llama_oversimplified

> **Almost all credit for this project belongs to
> [llama.cpp](https://github.com/ggml-org/llama.cpp), originally
> created by [Georgi Gerganov](https://github.com/ggerganov) and now
> maintained by the [ggml-org](https://github.com/ggml-org)
> organization and its contributors.** This repository is just a
> Docker wrapper plus a Python chat client around their work — it does
> not reimplement or improve on the inference engine itself. Please
> star, credit, and support the upstream project.

A locally hosted chatbot that serves GGUF language and vision models
via llama.cpp's `llama-server`, accessed with the OpenAI Python SDK.
The models run on your own hardware (NVIDIA GPU via CUDA); no external
chat API is ever contacted.

Two containerized services are defined by `docker-compose.yaml`:

- **`llama_cpp_server`** — the C++ `llama-server` binary, built in
  `llama_server/Dockerfile`, serving the OpenAI-compatible `/v1` API
  on an NVIDIA GPU.
- **`chat_client`** — the Python chatbot (`chatbot/workplace/`), which
  drives an interactive chat loop against the server.

> **Recommended: use the browser GUI instead of the Python client.**
> `llama-server` ships with its own web UI, served at
> `http://localhost:${PORT}` once the server container is running.
> For most day-to-day use, opening that in a browser is simpler and
> more reliable than the Python CLI client — the client here is more
> of a scriptable/example integration (tool calls, summarization,
> image references) than a polished primary interface. Use the client
> if you specifically want that scripted behavior; otherwise, the
> browser GUI is the easier way to just chat with a model.

This repository contains **deployment configuration, the Python
client, and run/download scripts only**. The actual C++ source is
cloned from the upstream `llama.cpp` repository at Docker build time
(see [Building](#building)).

## Repository layout

```
llama_oversimplified/
├── docker-compose.yaml         # GPU service definition
├── sample.env                  # template for .env
├── .env                        # runtime secrets (gitignored)
├── chatbot/
│   ├── Dockerfile
│   └── workplace/
│       ├── config.py                   # pydantic configs
│       ├── openAIclient.py             # CLI entrypoint + chat loop
│       ├── schemas.py                  # pydantic message schemas
│       ├── requirements.txt
│       ├── openAIchat/
│       │   ├── chat.py                 # message_in_chat, message_factory
│       │   ├── actions.py
│       │   ├── system_prompt.txt
│       │   └── temp.txt
│       ├── utils/
│       │   ├── helpers_functions.py    # image encoding, chat_to_model
│       │   ├── summary.py              # summarization + read_context tool
│       │   └── time_tracker.py
│       └── img_refferences/
│           └── image_refferences.py
└── llama_server/
    ├── Dockerfile               # multi-stage CUDA build
    ├── run_server/              # per-model launch scripts
    ├── download_scripts/        # model download scripts
    ├── logs/                    # server logs (tee'd)
    └── models/                  # model weights (gitignored)
```

The container mounts the host directories so config files, models, and
run scripts are visible both inside the container and on the host.

## Model directories

The directories under `llama_server/models/` are directories only;
actual GGUF weight files are gitignored (add them explicitly if you
must track them):

```
llama_server/models/
├── base_models/
├── coder/
├── draft_models/
└── mmproj/
```

## Prerequisites

- NVIDIA GPU with CUDA (driver + runtime)
- Docker, with the **NVIDIA Container Toolkit** installed so the
  server container can see the GPU
- A Hugging Face token (`HF_TOKEN`) to download the model weights

`aria2c` is used by the download scripts and is installed
automatically inside the llama-server Docker image — no need to
install it separately on the host.

## Configuration

Settings come from a `.env` file (see `sample.env`):

| Variable | Purpose |
| --- | --- |
| `HF_TOKEN` | Hugging Face token used to authenticate model downloads. |
| `PORT` | Host port mapped to the container's port (default `8081`). |
| `CUDA_VERSION` | Base image CUDA tag for the Docker build (e.g. `13.3.0`). Must match a CUDA version your NVIDIA driver supports — check with `nvidia-smi`. |

The server service sets `shm_size: '16g'`, required for large models.

## Build & run

```bash
# 1. Configure
cp sample.env .env
#    - HF_TOKEN:      your Hugging Face token
#    - PORT:          port to expose (default 8081)
#    - CUDA_VERSION:  base-image tag for the Docker build

# 2. Build and start (foreground, logs stream to your terminal)
docker compose up --build

# ...or start detached (runs in the background)
docker compose up --build -d
```

Once running:

- **Browser GUI (recommended):** open `http://localhost:${PORT}` in
  your browser.
- **OpenAI-compatible API:** available at `http://localhost:${PORT}/v1`.
- **Python chat client:** runs interactively as its own container (a
  `while True` CLI loop) — see [Chat flow](#chat-flow) below.

To stop everything:

```bash
docker compose down
```

## Accessing the running containers

First, find the container names/IDs:

```bash
docker ps
```

**Open an interactive shell** in either container:

```bash
docker exec -it <container_name> bash
```

**Run a single command directly from the host** without entering the
container first:

```bash
docker exec -it <container_name> <command>
```

## Chat flow

`chatbot/workplace/openAIclient.py` is the entrypoint — an interactive
CLI loop. Each user turn is appended to the chat history, sent to the
server through `message_in_chat` (`chat.py`), and the assistant
response is appended back. Once `MAX_MESSAGES` (100) messages
accumulate, `Summary.make_summary` collapses the oldest `REDUCE_BY`
(30) messages via a separate server call. Image references from
`img_refferences/` are prepended to every user message, and the
`read_context` tool exposes the long-term summary to the model.

## Downloading models

Model weights are GGUF files pulled from Hugging Face. The download
scripts use `aria2c` with your `HF_TOKEN`:

```bash
llama_server/download_scripts/download.bash
```

Models are saved to `llama_server/models/` (which is gitignored — add
them explicitly if you must track them).

## Building

The real C++ source is **not** committed here. The
`llama_server/Dockerfile` clones the upstream repository into the
build container:

```dockerfile
RUN git clone --recursive https://github.com/ggerganov/llama.cpp.git .
```

Build the image from the project root:

```bash
docker compose build
```

The Dockerfile compiles the server and CLI with CUDA enabled
(`-DGGML_CUDA=ON`, `-DCMAKE_CUDA_ARCHITECTURES=120`) and produces
`llama-server` / `llama-cli` binaries.

## Notes & gotchas

- **Source is remote.** There is no C++ source in this repository —
  it's cloned from `llama.cpp` at build time. To inspect or modify the
  actual inference code, clone the upstream repo and build from there.
- **`.env` is gitignored.** Don't commit secrets — copy `sample.env`
  to `.env` and fill in your own `HF_TOKEN`.
- **`llama_server/models/` is gitignored.** Model weights are
  downloaded or added separately, not committed.
- **A GPU is required at runtime.** The image and container are
  pinned to `nvidia/cuda` and request GPU access via Docker's
  `deploy.resources.reservations.devices`.
- **Base URLs use Docker service names**
  (`http://llama_cpp_server:8081/v1`). They only resolve inside the
  `docker compose` network; the Python client won't reach the server
  when run outside Docker.
- **`system_prompt.txt` ships empty.** A working system prompt must be
  written to `chatbot/workplace/openAIchat/system_prompt.txt` before
  the chat loop produces meaningful output.
- **The browser GUI needs none of the above client setup.** If you
  just want to chat with a model, the server's own web UI at
  `http://localhost:${PORT}` works out of the box once the server
  container is up — no Python client, system prompt file, or extra
  configuration required.

## Credits & License

All the actual inference work here is done by
[llama.cpp](https://github.com/ggml-org/llama.cpp), created by
[Georgi Gerganov](https://github.com/ggerganov) and now maintained by
the [ggml-org](https://github.com/ggml-org) organization and its
contributors. This repository is nothing more than a thin Docker
wrapper plus a Python client around it — the Dockerfiles, configs,
launch/download scripts, and client code are the only things original
to this repo.

**llama.cpp itself is MIT licensed.** This wrapper repo doesn't change
or override that — you're bound by its license and terms, not just
this repo's.

**⚠️ Individual models are licensed separately, and some are
restrictive.** llama.cpp supports many different model families, each
released under its own license by its own authors. These are **not**
all permissive — some, including certain versions of Meta's Llama
weights, carry usage or scale-based restrictions, and various
community GGUF conversions inherit non-commercial or other restrictive
terms from their source model. Before using any model downloaded
through this project:

- Check that specific model's license and usage terms (commercial-use
  restrictions, redistribution terms, generated-content terms, etc.)
- Don't assume MIT (llama.cpp's license) extends to every model it can
  load — it doesn't
- When in doubt, check the model's page on Hugging Face or wherever it
  was sourced from

If you use this project, please:

- Respect the [llama.cpp license and
  documentation](https://github.com/ggml-org/llama.cpp) for anything
  related to the inference engine itself
- Direct bug reports or feature requests about the inference engine
  itself upstream to llama.cpp, not this repo — this repo only wraps
  it in Docker plus the Python client
