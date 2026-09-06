MODEL="/app/models/coder/qwen2.5-coder-32b-instruct-q4_k_m.gguf"
SERVER="/src/llama-server"

mkdir -p /app/logs

$SERVER \
  --model $MODEL \
  --n-gpu-layers -1 \
  --ctx-size 8192 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --batch-size 512 \
  --ubatch-size 512 \
  --flash-attn on \
  --parallel 1 \
  --cont-batching \
  --port "$PORT" \
  --host 0.0.0.0 2>&1 | tee /app/logs/autocomplete-server.log
