set -euo pipefail

. /app/download_scripts/download.bash

download \
    "https://huggingface.co/llmfan46/Qwen3.6-35B-A3B-uncensored-heretic-GGUF/resolve/main/Qwen3.6-35B-A3B-uncensored-heretic-Q5_K_M.gguf" \
    "coder/Qwen3.6-35B-A3B-uncensored-heretic-Q5_K_M.gguf" \
    8 &

download \
    "https://huggingface.co/llmfan46/Qwen3.6-35B-A3B-uncensored-heretic-GGUF/resolve/main/Qwen3.6-35B-A3B-uncensored-heretic-mmproj-BF16.gguf" \
    "mmproj/Qwen3.6-35B-A3B-uncensored-heretic-mmproj-BF16.gguf" \
    8 &


wait

echo "All downloads finished."k
