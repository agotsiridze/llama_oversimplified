MODEL="/app/models/base_models/gemma-4-31B-it-uncensored-heretic-Q5_K_M.gguf"
DRAFT="/app/models/draft_models/gemma-4-E4B-it-ultra-uncensored-heretic-Q4_K_M.gguf"
SERVER="/src/llama-server"


$SERVER \
  --model $MODEL \
  --model-draft $DRAFT \
  --n-gpu-layers -1 \
  --n-gpu-layers-draft -1 \
  --ctx-size 32768 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --batch-size 2048 \
  --ubatch-size 512 \
  --flash-attn on \
  --parallel 1 \
  --cont-batching \
  --spec-draft-n-max 8 \
  --draft-p-min 0.2 \
  --reasoning off \
  --port "$PORT" \
  --host 0.0.0.0 2>&1 | tee /app/logs/server.log

  # --chat-template-kwargs '{"enable_thinking":false}' \
