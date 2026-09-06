set -euo pipefail

. /app/download_scripts/download.bash

download \
    "https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct-GGUF/resolve/main/qwen2.5-coder-32b-instruct-q4_k_m.gguf" \
    "coder/qwen2.5-coder-32b-instruct-q4_k_m.gguf" \
    8 &

download \
    "https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF/resolve/main/nomic-embed-text-v1.5.f16.gguf" \
    "rag/nomic-embed-text-v1.5.f16.gguf" \
    8 &


wait

echo "All downloads finished."
