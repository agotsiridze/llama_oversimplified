set -euo pipefail

. /app/download_scripts/download.bash

download \
    "https://huggingface.co/llmfan46/gemma-4-31B-it-uncensored-heretic-GGUF/resolve/main/gemma-4-31B-it-uncensored-heretic-Q5_K_M.gguf" \
    "base_models/gemma-4-31B-it-uncensored-heretic-Q5_K_M.gguf" \
    8 &

download \
    "https://huggingface.co/llmfan46/gemma-4-31B-it-uncensored-heretic-GGUF/resolve/main/gemma-4-31B-it-uncensored-heretic-Q6_K.gguf" \
    "base_models/gemma-4-31B-it-uncensored-heretic-Q6_K.gguf" \
    4 &

download \
    "https://huggingface.co/llmfan46/gemma-4-31B-it-uncensored-heretic-GGUF/resolve/main/gemma-4-31B-it-mmproj-BF16.gguf" \
    "mmproj/gemma-4-31B-it-mmproj-BF16.gguf" \
    4 &

download \
    "https://huggingface.co/llmfan46/gemma-4-E4B-it-ultra-uncensored-heretic-GGUF/resolve/main/gemma-4-E4B-it-ultra-uncensored-heretic-Q4_K_M.gguf" \
    "draft_models/gemma-4-E4B-it-ultra-uncensored-heretic-Q4_K_M.gguf" \
    4 &


wait

echo "All downloads finished."
