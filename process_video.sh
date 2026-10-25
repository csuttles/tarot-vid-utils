#!/bin/bash

# Exit immediately if any command in the pipeline fails
set -e

# Verify a file path argument was actually passed
if [ -z "$1" ]; then
    echo "Usage: ./process_video.sh <path_to_video>"
    exit 1
fi

VIDEO_PATH="$1"
BASE_PATH="${VIDEO_PATH%.*}"
SRT_PATH="${BASE_PATH}.srt"
RAW_CHAPTERS_PATH="${BASE_PATH}_chapters_raw.txt"
POLISHED_CHAPTERS_PATH="${BASE_PATH}_chapters.txt"
YOUTUBE_META_PATH="${BASE_PATH}_youtube_meta.md"

echo "=========================================================================="
echo "🔮 Kicking Off Master Tarot Video Processing Pipeline"
echo "=========================================================================="

# Step 1: Dialogue Extraction via faster-whisper
echo -e "\n🎬 [Step 1/3] Transcribing Audio Track via faster-whisper..."
poetry run python src/tarot_vid_tools/extract_subs.py \
    "$VIDEO_PATH" \
    --device cpu \
    --compute-type int8 \
    --threads 8

# Step 2: Custom Tarot Chapter / Card Milestone Marker Parse
echo -e "\n🃏 [Step 2/3] Analyzing Text Timelines for Card Signatures..."
if [ -f "$SRT_PATH" ]; then
    poetry run tarot-chapters parse "$SRT_PATH" --output "$RAW_CHAPTERS_PATH"
else
    echo "Error: Target SRT file was not created successfully."
    exit 1
fi

# Step 3: Polish Chapters Locally using Ollama to kill repetitive phrasing
echo -e "\n✨ Refining and condensing chapters via Ollama..."
POLISH_PROMPT="You are a professional editor. Clean up the following YouTube video chapters. Group multiple deck listings for the same card into a single, punchy phrase. Strip out repetitive phrasing like 'grounding structured archetypal currents directly through the element of'. Make each line unique, deeply evocative, and specific to the cards mentioned. Keep the exact 'hh:mm:ss - Title' format intact. Zero emojis. Raw text lines only:\n\n$(cat "$RAW_CHAPTERS_PATH")"

curl -s -X POST http://localhost:11434/api/chat -d "{
  \"model\": \"llama3.2:latest\",
  \"messages\": [
    {\"role\": \"user\", \"content\": \"$(echo "$POLISH_PROMPT" | sed 's/"/\\"/g' | tr '\n' ' ')\"}
  ],
  \"stream\": false
}" | python3 -c "import sys, json; print(json.load(sys.stdin)['message']['content'])" > "$POLISHED_CHAPTERS_PATH"

# Step 4: Local YouTube Asset Packaging via Ollama
echo -e "\n📊 [Step 3/3] Compiling Local Metadata Package via Ollama..."
if [ -f "$SRT_PATH" ]; then
    poetry run python src/tarot_vid_tools/generate_yt_metadata_local.py \
        "$SRT_PATH" \
        -m "llama3.2:latest"
else
    echo "Error: Target SRT file missing before metadata packaging loop."
    exit 1
fi

# Step 5: Combine Analytics Outputs into final Markdown file
if [ -f "$POLISHED_CHAPTERS_PATH" ]; then
    echo -e "\nAppending dense polished chapters to final markdown workspace profile..."
    echo -e "\n\n## 🏷️ Extracted Structural Video Chapters\n\`\`\`text" >> "$YOUTUBE_META_PATH"
    cat "$POLISHED_CHAPTERS_PATH" >> "$YOUTUBE_META_PATH"
    echo -e "\`\`\`" >> "$YOUTUBE_META_PATH"
fi

# Clean up raw artifacts
rm -f "$RAW_CHAPTERS_PATH"

echo "=========================================================================="
echo "🎉 Pipeline Completed Successfully!"
echo "=========================================================================="

