"""Module for extracting audio from video files and generating SRT subtitles.

Uses FFmpeg for audio preprocessing and OpenAI's Whisper for local transcription.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import whisper
from whisper.utils import get_writer


class SystemDependencyError(Exception):
    """Raised when a required system-level binary is missing or fails."""
    pass


class VideoTranscriber:
    """Handles the translation pipeline from video input to SRT subtitle files."""

    def __init__(self, model_name: str = "base") -> None:
        """Initializes the transcriber with a specific Whisper model layout.

        Args:
            model_name: The size/variant of the Whisper model to load
                       (e.g., 'tiny', 'base', 'small', 'medium', 'large').
        """
        self.model_name: str = model_name
        self._model: Optional[whisper.Whisper] = None

    @property
    def model(self) -> whisper.Whisper:
        """Lazy-loads the Whisper model state into memory upon first call."""
        if self._model is None:
            print(f"Loading Whisper '{self.model_name}' model into memory...")
            self._model = whisper.load_model(self.model_name)
        return self._model

    def _extract_audio(self, video_path: Path, temp_audio_path: Path) -> None:
        """Preprocesses video inputs to extract mono 16kHz audio via FFmpeg.

        Args:
            video_path: System filesystem location of source file asset.
            temp_audio_path: Target filesystem location for intermediate wav binary.

        Raises:
            SystemDependencyError: If FFmpeg binary executable is unreachable or halts.
        """
        print(f"Extracting raw audio channel track to: {temp_audio_path.name}...")

        ffmpeg_cmd = [
            "ffmpeg", "-i", str(video_path),
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            str(temp_audio_path), "-y"
        ]

        try:
            subprocess.run(
                ffmpeg_cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as err:
            raise SystemDependencyError(
                "FFmpeg pipeline failure. Verify system installation with: brew install ffmpeg"
            ) from err

    def process(self, video_path: Path, output_dir: Optional[Path] = None) -> Path:
        """Executes the conversion pipeline from localized source video to SRT file.

        Args:
            video_path: System path targeting source file payload (.mov, .mp4, etc.).
            output_dir: Explicit output folder. Defaults to the video file's parent folder.

        Returns:
            Path: Filesystem location where final SRT document asset was written.
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Source media target layout not found: {video_path}")

        target_dir: Path = output_dir if output_dir else video_path.parent
        srt_output_path: Path = target_dir / f"{video_path.stem}.srt"
        temp_audio_path: Path = video_path.parent / f"_{video_path.stem}_temp.wav"

        try:
            # 1. Pipeline preparation
            self._extract_audio(video_path, temp_audio_path)

            # 2. Local Model Transcription Execution
            print("Processing audio track transcription segments...")
            transcription_data: Dict[str, Any] = self.model.transcribe(str(temp_audio_path))

            # 3. Output Generation Realization
            print(f"Serializing textual sub-frames -> {srt_output_path}")
            writer = get_writer("srt", str(target_dir))
            writer(transcription_data, str(temp_audio_path))

        finally:
            # Enforce clean-up tracking over ephemeral binary products
            if temp_audio_path.exists():
                os.remove(temp_audio_path)

        return srt_output_path


def main() -> None:
    """Configures explicit validation runtimes over incoming application calls."""
    parser = argparse.ArgumentParser(
        description="Convert localized video assets (.mov, .mp4) to standard .srt subtitle files using local machine learning inference.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "video_path",
        type=str,
        help="Path targeting the target source video input file on the local machine."
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="deepdml/faster-whisper-large-v3-turbo-ct2",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model footprint variation to load. Larger versions improve transcription clarity at the expense of local compute speeds."
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default=None,
        help="Directory route override targeting where sub-frame .srt logs should live. If omitted, matching file paths are preserved."
    )

    args = parser.parse_args()

    video_file = Path(args.video_path)
    output_folder = Path(args.output_dir) if args.output_dir else None

    try:
        transcriber = VideoTranscriber(model_name=args.model)
        final_srt = transcriber.process(video_file, output_dir=output_folder)
        print(f"Success! Artifact compiled cleanly to: {final_srt.resolve()}")
    except (FileNotFoundError, SystemDependencyError) as error:
        print(f"\nExecution Error: {error}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user exit instruction.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()

