MODEL="/app/models/base_models/gemma-4-31B-it-uncensored-heretic-Q6_K.gguf"
MMPROJ="/app/models/mmproj/gemma-4-31B-it-mmproj-BF16.gguf"
SERVER="/src/llama-server"

mkdir -p /app/logs

$SERVER \
  --model $MODEL \
  --mmproj $MMPROJ \
  --n-gpu-layers -1 \
  --ctx-size 32768 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --batch-size 512 \
  --ubatch-size 512 \
  --flash-attn on \
  --parallel 1 \
  --cont-batching \
  --reasoning off \
  --port "$PORT" \
  --host 0.0.0.0 2>&1 | tee /app/logs/server.log
