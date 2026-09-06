SERVER="/src/llama-server"
MODEL="/app/models/base_models/Ornith-1.0-35B-heretic-Q6_K.gguf"
MMPROJ="/app/models/mmproj/mmproj-Ornith-1.0-35B-heretic-Q8_0.gguf"

$SERVER \
  --model "$MODEL" \
  --mmproj "$MMPROJ" \
  --n-gpu-layers -1 \
  --ctx-size 32768 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --flash-attn on \
  --no-mmap \
  --parallel 1 \
  --cont-batching \
  --port "$PORT" \
  --host 0.0.0.0 2>&1 | tee /app/logs/server.log
