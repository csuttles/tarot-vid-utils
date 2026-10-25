"""Module for extracting video dialogue into SRT subtitles using faster-whisper.

This script utilizes CTranslate2-optimized Whisper models to transcribe audio
from video files, leveraging multi-core CPUs or hardware accelerators.
"""

import argparse
import os
import sys
from typing import Optional
from faster_whisper import WhisperModel


def format_srt_timestamp(seconds: float) -> str:
    """Converts a duration in seconds into a standard SRT timestamp string.

    Args:
        seconds: The time in seconds.

    Returns:
        A string formatted as 'HH:MM:SS,mmm'.
    """
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int(round((seconds % 1) * 1000))
    if millisecs >= 1000:
        millisecs -= 1000
        secs += 1
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millisecs:03d}"


def process_audio_dialogue(
    video_path: str,
    output_path: str,
    model_name: str,
    device: str,
    compute_type: str,
    threads: int,
) -> None:
    """Transcribes video audio streams and outputs a structured SRT file.

    Args:
        video_path: Path to the source video file (.mov, .mp4, etc).
        output_path: Destination path for the generated SRT file.
        model_name: The HuggingFace/CTranslate2 Whisper model key identifier.
        device: Computational device framework ('cpu', 'cuda').
        compute_type: Quantization rate ('float16', 'int8', 'int8_float16').
        threads: Number of worker threads utilized for CPU execution.
    """
    if not os.path.exists(video_path):
        print(f"Error: Input file does not exist: {video_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading Model : {model_name} on [{device.upper()}]...")

    # Initialize the Whisper engine with custom hardware configurations
    model = WhisperModel(
        model_size_or_path=model_name,
        device=device,
        compute_type=compute_type,
        cpu_threads=threads,
    )

    print(f"Processing    : {video_path}")
    print(f"Output Target : {output_path}")
    print("Transcribing video dialogue tracks (this may take a moment)...")

    # transcribe directly extracts audio from the container (no manual ffmpeg step needed)
    segments, info = model.transcribe(video_path, beam_size=5)

    print(f"Detected language: '{info.language}' (probability: {info.language_probability:.2f})")

    with open(output_path, "w", encoding="utf-8") as srt_file:
        for idx, segment in enumerate(segments, start=1):
            start_time = format_srt_timestamp(segment.start)
            end_time = format_srt_timestamp(segment.end)
            text = segment.text.strip()

            srt_file.write(f"{idx}\n{start_time} --> {end_time}\n{text}\n\n")

    print(f"Finished! Successfully generated subtitle track configuration.")


def main() -> None:
    """Parses execution parameters and manages configuration defaults."""
    parser = argparse.ArgumentParser(
        description="Extract video dialogue channels into SRT subtitle files using faster-whisper."
    )

    parser.add_argument(
        "video_path", type=str, help="Path to the input video file."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Path to save the generated .srt file. Defaults to alongside the input file.",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="eepdml/faster-whisper-large-v3-turbo-ct2",
        help="CTranslate2 Whisper model choice identifier.",
    )
    parser.add_argument(
        "-d",
        "--device",
        type=str,
        choices=["cpu", "cuda"],
        default="cpu",
        help="Target processing hardware backend container platform.",
    )
    parser.add_argument(
        "-c",
        "--compute-type",
        type=str,
        default="int8",
        help="Quantization type (e.g., 'int8' for CPU, 'float16' for GPU/CUDA).",
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=4,
        help="Total worker core allocation threads assigned to CPU processing blocks.",
    )

    args = parser.parse_args()

    if not args.output:
        base_path, _ = os.path.splitext(args.video_path)
        args.output = f"{base_path}.srt"

    process_audio_dialogue(
        video_path=args.video_path,
        output_path=args.output,
        model_name=args.model,
        device=args.device,
        compute_type=args.compute_type,
        threads=args.threads,
    )


if __name__ == "__main__":
    main()

