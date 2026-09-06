set -euo pipefail

. /app/download_scripts/download.bash

download \
    "https://huggingface.co/skinnyctax/Ornith-1.0-35B-Q6_K-Frankenstein-MTP-GGUF/resolve/main/ornith-1.0-35b-Q6_K-MTP-donor-heads.gguf" \
    "draft_models/ornith-1.0-35b-Q6_K-MTP-donor-heads.gguf" \
    8 &

download \
    "https://huggingface.co/thanet-s/Ornith-1.0-35B-heretic-gguf/resolve/main/mmproj-Ornith-1.0-35B-heretic-Q8_0.gguf" \
    "mmproj/mmproj-Ornith-1.0-35B-heretic-Q8_0.gguf" \
    8 &


wait

echo "All downloads finished."
