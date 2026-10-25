"""Unit test suite for the video subtitle extraction script.

This module validates timestamp formatting, video dialogue streaming logic, SRT
file building formatting, and correct error handling pathways.
"""

import pytest
# ... (rest of the file remains exactly the same)

import argparse  # <-- Add this missing import
import os
import sys
from typing import Generator
from unittest.mock import MagicMock, mock_open, patch

import pytest
from tarot_vid_tools.extract_subs import (
    format_srt_timestamp,
    main,
    process_audio_dialogue,
)


@pytest.fixture
def mock_video_path(tmp_path) -> str:
    """Fixture to create a fake input video file path for structural checks."""
    video = tmp_path / "mock_video.mov"
    video.touch()
    return str(video)


@pytest.fixture
def mock_output_path(tmp_path) -> str:
    """Fixture to provide a clean target destination for expected SRT files."""
    return str(tmp_path / "mock_video.srt")


def test_format_srt_timestamp_standard() -> None:
    """Validates basic parsing conversion from raw float values into standard SRT formats."""
    # Test standard baseline value
    assert format_srt_timestamp(0.0) == "00:00:00,000"

    # Test standard complex time parsing mapping values
    assert format_srt_timestamp(3661.123) == "01:01:01,123"


def test_format_srt_timestamp_rounding() -> None:
    """Verifies precision rounding loops for fractional float millisecond boundaries."""
    # Test high repeating fraction round-ups
    assert format_srt_timestamp(0.9999) == "00:00:01,000"

    # Test truncation variations
    assert format_srt_timestamp(125.4567) == "00:02:05,457"


@patch("tarot_vid_tools.extract_subs.WhisperModel")
def test_process_audio_dialogue_success(
    mock_whisper_class: MagicMock, mock_video_path: str, mock_output_path: str
) -> None:
    """Validates the text mapping streaming loop when a model transcribes segments."""
    # Configure fake container structures returned from whisper generator loops
    mock_model_instance = MagicMock()
    mock_whisper_class.return_value = mock_model_instance

    mock_segment_1 = MagicMock()
    mock_segment_1.start = 1.500
    mock_segment_1.end = 4.250
    mock_segment_1.text = " Hello and welcome. "

    mock_segment_2 = MagicMock()
    mock_segment_2.start = 5.100
    mock_segment_2.end = 7.900
    mock_segment_2.text = "Today we read tarot cards."

    mock_info = MagicMock()
    mock_info.language = "en"
    mock_info.language_probability = 0.98

    # Mock out transcribe method execution yield paths
    mock_model_instance.transcribe.return_value = (
        [mock_segment_1, mock_segment_2],
        mock_info,
    )

    # Execute functional loop logic blocks
    process_audio_dialogue(
        video_path=mock_video_path,
        output_path=mock_output_path,
        model_name="mock-model",
        device="cpu",
        compute_type="int8",
        threads=4,
    )

    # Verify model initialization was called with constraints
    mock_whisper_class.assert_called_once_with(
        model_size_or_path="mock-model",
        device="cpu",
        compute_type="int8",
        cpu_threads=4,
    )

    # Assert correct SRT writing layouts matching standards
    assert os.path.exists(mock_output_path)
    with open(mock_output_path, "r", encoding="utf-8") as f:
        content = f.read()

    expected_srt = (
        "1\n"
        "00:00:01,500 --> 00:00:04,250\n"
        "Hello and welcome.\n\n"
        "2\n"
        "00:00:05,100 --> 00:00:07,900\n"
        "Today we read tarot cards.\n\n"
    )
    assert content == expected_srt


@patch("tarot_vid_tools.extract_subs.os.path.exists")
def test_process_audio_dialogue_missing_file(mock_exists: MagicMock) -> None:
    """Verifies process termination patterns when targeting broken non-existent video files."""
    mock_exists.return_value = False

    with pytest.raises(SystemExit) as exit_info:
        process_audio_dialogue(
            video_path="invalid.mov",
            output_path="invalid.srt",
            model_name="mock",
            device="cpu",
            compute_type="int8",
            threads=4,
        )
    assert exit_info.value.code == 1


@patch("tarot_vid_tools.extract_subs.argparse.ArgumentParser.parse_args")
@patch("tarot_vid_tools.extract_subs.process_audio_dialogue")
def test_main_cli_argument_forwarding(
    mock_process: MagicMock, mock_parse_args: MagicMock
) -> None:
    """Validates that parsed arguments and dynamic fallback defaults propagate perfectly inside main."""
    # Simulate arguments passed to CLI layout definitions
    mock_parse_args.return_value = argparse.Namespace(
        video_path="/path/to/vid.mp4",
        output=None,  # Implicitly triggers fallback path logic
        model="custom-model-id",
        device="cuda",
        compute_type="float16",
        threads=8,
    )

    main()

    # Verify output name auto-derived by swapping extensions
    mock_process.assert_called_once_with(
        video_path="/path/to/vid.mp4",
        output_path="/path/to/vid.srt",
        model_name="custom-model-id",
        device="cuda",
        compute_type="float16",
        threads=8,
    )

