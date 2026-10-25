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
CHAPTERS_PATH="${BASE_PATH}_chapters.txt"
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
    # Parse text sequences using auto-detection across local cached registries
    poetry run tarot-chapters parse "$SRT_PATH" --output "$CHAPTERS_PATH"
else
    echo "Error: Target SRT file was not created successfully."
    exit 1
fi

# Step 3: Local YouTube Asset Packaging via Ollama
echo -e "\n📊 [Step 3/3] Compiling Local Metadata Package via Ollama..."
if [ -f "$SRT_PATH" ]; then
    poetry run python src/tarot_vid_tools/generate_yt_metadata_local.py \
        "$SRT_PATH" \
        -m "llama3.2:latest"
else
    echo "Error: Target SRT file missing before metadata packaging loop."
    exit 1
fi

# Step 4: Combine Analytics Outputs for absolute convenience
if [ -f "$CHAPTERS_PATH" ]; then
    echo -e "\nAppending dense structural chapters to final markdown workspace profile..."
    echo -e "\n\n## 🏷️ Extracted Structural Video Chapters\n\`\`\`text" >> "$YOUTUBE_META_PATH"
    cat "$CHAPTERS_PATH" >> "$YOUTUBE_META_PATH"
    echo -e "\`\`\`" >> "$YOUTUBE_META_PATH"
fi

echo -e "\n=========================================================================="
echo "🎉 Pipeline Completed Successfully!"
echo "Generated SRT      : $SRT_PATH"
echo "Generated Chapters : $CHAPTERS_PATH"
echo "Generated YouTube  : $YOUTUBE_META_PATH"
echo "=========================================================================="

