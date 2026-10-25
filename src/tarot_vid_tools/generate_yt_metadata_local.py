"""Module for generating optimized YouTube video metadata locally using Ollama.

This script parses a SubRip (.srt) subtitle file, extracts the text timeline,
and dispatches it to a local Ollama LLM instance to output clean, unspammy titles,
descriptions, thumbnail ideas, and structured video chapters.
"""

import argparse
import os
import re
import sys
from typing import List, Optional
import requests


def parse_srt_to_text(srt_path: str) -> str:
    """Parses a standard SRT file to extract raw dialogue with approximate timelines.

    Args:
        srt_path: Absolute or relative path to the source .srt file.

    Returns:
        A compiled string layout of chronological text lines.
    """
    if not os.path.exists(srt_path):
        print(f"Error: Target SRT file missing: {srt_path}", file=sys.stderr)
        sys.exit(1)

    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.strip().split("\n\n")
    cleaned_timeline: List[str] = []

    for block in blocks:
        lines = block.split("\n")
        if len(lines) >= 3:
            timestamp = lines[1]
            match = re.match(r"(\d{2}:\d{2}:\d{2})", timestamp)
            time_str = match.group(1) if match else "00:00:00"
            text_content = " ".join(lines[2:])
            cleaned_timeline.append(f"[{time_str}] {text_content}")

    return "\n".join(cleaned_timeline)


def compile_metadata_package_local(transcript_data: str, model_name: str, host_url: str) -> str:
    """Dispatches the transcription blueprint to a local Ollama Chat instance.

    Enforces strict anti-spam parameters, banning emojis and generic clickbait phrasing.

    Args:
        transcript_data: Raw timestamped transcript text block.
        model_name: The local Ollama model identifier to target.
        host_url: The local loopback API address for the Ollama server.

    Returns:
        Structured text containing non-spammy YouTube titles, descriptions, and chapters.
    """
    # Strict behavioral boundary setup to filter local LLM marketing fluff
    system_prompt = (
        "You are an authentic, clear, and professional writer specializing in tarot, archetypes, and spiritual content. "
        "Your task is to analyze a timestamped transcript and generate a clean, minimal YouTube Metadata Package for cjef.\n\n"
        "STRICT ANTI-SPAM FORMATTING RULES:\n"
        "1. DO NOT use ANY emojis anywhere in the output. Zero emojis.\n"
        "2. DO NOT use corporate marketing jargon, hype, or generic clickbait words (e.g., 'unleash', 'ultimate', 'game-changing', 'transformative').\n"
        "3. DO NOT include generic call-to-action scripts like 'Don't forget to like, subscribe, smash that bell, or comment below!'\n"
        "4. Keep the text grounded, articulate, calm, and accurate to what was actually spoken.\n"
        "5. Limit hashtags to a maximum of 3 highly specific terms at the absolute end of the description."
    )

    user_prompt = f"""
    Analyze the following timestamped video transcript and generate a grounded YouTube Video Metadata Package for cjef.

    TRANSCRIPT DATA:
    \"\"\"
    {transcript_data}
    \"\"\"

    Please generate the following distinct sections, keeping them clean, accurate, and completely aligned with the transcript:

    1. **VIDEO TITLES (Provide 3 distinct options without emojis)**:
       - Option A: Curiosity/Insight-driven (clear, human-centric hook without using clickbait buzzwords).
       - Option B: Search-focused (direct and simple keywords matching the core topic).
       - Option C: Esoteric/Archetypal (focusing on the cards or energy dynamics discussed).

    2. **THUMBNAIL TEXT CONCEPTS (Provide 2-3 short, punchy 2-4 word phrases)**:
       - Text options that can overlay graphics easily. Do not use quotation marks in the suggestions.

    3. **CLEAN VIDEO DESCRIPTION**:
       - Provide a minimal 2-3 sentence introductory summary explaining what is covered in the video based on the transcript.
       - Provide a clean, bulleted list of the exact cards pulled or core themes discussed.
       - End with exactly 3 relevant hashtags on a single line. No call-to-action fluff.

    4. **ACCURATE VIDEO CHAPTERS (Mandatory Format: hh:mm:ss - Chapter Title)**:
       - Map precise timestamps where shifts, layout drops, or new card explanations occur.
       - Use clean, professional formatting (e.g., '00:04:12 - The Fool: Overcoming Hesitation' instead of '00:04:12 - !! WOW THE FOOL REVEALED !!').
       - The very first chapter must start exactly at 00:00:00.
    """

    print(f"Connecting to local Ollama host engine running [{model_name}]...")

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.15,      # Dropped very low to keep the model strictly factual
            "top_k": 20,              # Limits the model from wandering off into random marketing vocabulary
            "presence_penalty": 0.0,
            "frequency_penalty": 0.5  # Penalizes repetitive corporate phrases
        }
    }

    try:
        response = requests.post(f"{host_url}/api/chat", json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "")
    except requests.exceptions.RequestException as e:
        print(f"\nError: Could not process text via Ollama Chat API.\nDetails: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Manages system arguments and coordinates file pipeline generation pathways."""
    parser = argparse.ArgumentParser(
        description="Transform raw SRT files into clean, unspammy YouTube metadata profiles locally using Ollama."
    )
    parser.add_argument(
        "srt_path", type=str, help="Path to the generated source .srt file."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Path to save the generated text documentation. Defaults next to input file.",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="llama3.2:latest",  # Natively pinned as your project default
        help="Ollama model string token signature. (Default: llama3.2:latest)",
    )
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:11434",
        help="Ollama server service base loopback endpoint. (Default: http://localhost:11434)",
    )

    args = parser.parse_args()

    if not args.output:
        base_path, _ = os.path.splitext(args.srt_path)
        args.output = f"{base_path}_youtube_meta.md"

    print(f"Reading timestamps from: {args.srt_path}")
    transcript = parse_srt_to_text(args.srt_path)

    metadata_package = compile_metadata_package_local(
        transcript_data=transcript,
        model_name=args.model,
        host_url=args.url
    )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(metadata_package)

    print(f"\n🎉 Success! Clean local YouTube asset packaging complete.")
    print(f"Saved directly to: {args.output}")


if __name__ == "__main__":
    main()

