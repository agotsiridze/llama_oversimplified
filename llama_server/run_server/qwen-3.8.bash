MODEL="/app/models/base_models/Qwen3.8-27B-Unleashed-UD-Q6_K.gguf"
SERVER="/src/llama-server"
MMPROJ="/app/models/mmproj/qwen-3.8-mmproj-Unleashed-f16.gguf"


$SERVER \
  --model $MODEL \
  --mmproj $MMPROJ \
  --n-gpu-layers -1 \
  --n-gpu-layers-draft -1 \
  --ctx-size 131072 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --batch-size 2048 \
  --ubatch-size 512 \
  --flash-attn on \
  --parallel 1 \
  --cont-batching \
  --spec-draft-n-max 8 \
  --draft-p-min 0.2 \
  --port "$PORT" \
  --host 0.0.0.0 2>&1 | tee /app/logs/server.log

