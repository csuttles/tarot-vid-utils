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

echo "=========================================================================="
echo "🔮 Kicking Off Tarot Video Pipeline"
echo "=========================================================================="

# Step 1: Run Audio Dialogue Subtitle Extraction via faster-whisper
echo -e "\n🎬 [Step 1/2] Transcribing Dialogue Channels..."
poetry run python src/tarot_vid_tools/extract_subs.py \
    "$VIDEO_PATH" \
    --device cpu \
    --compute-type int8 \
    --threads 8

# Step 2: Generate Unspammy YouTube Metadata Assets via Local Ollama
echo -e "\n📊 [Step 2/2] Compiling YouTube Asset Descriptions via Ollama..."
if [ -f "$SRT_PATH" ]; then
    poetry run python src/tarot_vid_tools/generate_yt_metadata_local.py \
        "$SRT_PATH" \
        -m "llama3.2:latest"
else
    echo "Error: Target SRT file was not created successfully."
    exit 1
fi

echo -e "\n=========================================================================="
echo "🎉 Pipeline Completed Successfully!"
echo "Generated SRT : $SRT_PATH"
echo "Generated MD  : ${BASE_PATH}_youtube_meta.md"
echo "=========================================================================="

