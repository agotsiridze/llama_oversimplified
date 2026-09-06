set -euo pipefail

. /app/download_scripts/download.bash

download \
    "https://huggingface.co/ornith-ai/Ornith-1.5-35B-A3B-GGUF/resolve/main/Ornith-1.5-35B-Q4_K_M.gguf" \
    "base_models/Ornith-1.5-35B-Q4_K_M.gguf" \
    8 &

download \
    "https://huggingface.co/ornith-ai/Ornith-1.5-35B-A3B-GGUF/resolve/main/mmproj-Ornith-1.5-35B-BF16.gguf" \
    "mmproj/mmproj-Ornith-1.5-35B-BF16.gguf" \
    8 &


wait

echo "All downloads finished."
