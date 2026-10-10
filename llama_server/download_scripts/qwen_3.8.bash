set -euo pipefail

. /app/download_scripts/download.bash

# download \
#     "https://huggingface.co/outsourc-e/Qwen3.8-27B-Unleashed-GGUF/resolve/main/Qwen3.8-27B-Unleashed-UD-Q6_K.gguf" \
#     "base_models/Qwen3.8-27B-Unleashed-UD-Q6_K.gguf" \
#     8 &
download \
    "https://huggingface.co/outsourc-e/Qwen3.8-27B-Unleashed-GGUF/resolve/main/mmproj-Unleashed-f16.gguf" \
    "mmproj/qwen-3.8-mmproj-Unleashed-f16.gguf" \
    16 &


wait

echo "All downloads finished."
