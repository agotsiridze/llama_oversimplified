download() {
    local url="$1"
    local output="$2"
    local threads="$3"

    aria2c \
        -c \
        -x "$threads" \
        -s "$threads" \
        -k 1M \
        --header "Authorization: Bearer ${HF_TOKEN}" \
        "$url" \
        -d /app/models/ \
        -o "$output"
}
