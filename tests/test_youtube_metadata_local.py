"""Unit test suite verifying local execution patterns inside the Ollama pipeline."""

import argparse
import os
from unittest.mock import MagicMock, patch
import pytest
import requests
from tarot_vid_tools.generate_yt_metadata_local import compile_metadata_package_local, main


@patch("tarot_vid_tools.generate_yt_metadata_local.requests.post")
def test_compile_metadata_package_local_success(mock_post: MagicMock) -> None:
    """Verifies that json payloads pack down correctly over standard network responses."""
    mock_response = MagicMock()
    # Updated to match the nested dict returned by the chat API configuration
    mock_response.json.return_value = {"message": {"content": "### Local Mock Output"}}
    mock_post.return_value = mock_response

    result = compile_metadata_package_local("Mock Transcript", "llama3.2", "http://localhost:11434")
    assert result == "### Local Mock Output"


@patch("tarot_vid_tools.generate_yt_metadata_local.argparse.ArgumentParser.parse_args")
@patch("tarot_vid_tools.generate_yt_metadata_local.compile_metadata_package_local")
@patch("tarot_vid_tools.generate_yt_metadata_local.parse_srt_to_text")
def test_main_local_flow_execution(
    mock_parse_srt: MagicMock, mock_compile: MagicMock, mock_parse_args: MagicMock, tmp_path
) -> None:
    """Validates that file endpoints link correctly on disk during local main calls."""
    target_srt = tmp_path / "test_vid_local.srt"
    target_srt.touch()

    mock_parse_args.return_value = argparse.Namespace(
        srt_path=str(target_srt),
        output=None,
        model="llama3.2",
        url="http://localhost:11434"
    )

    mock_parse_srt.return_value = "[00:00:00] Sample text content lines."
    mock_compile.return_value = "### Complete Local Metadata Suite"

    main()

    expected_output_path = tmp_path / "test_vid_local_youtube_meta.md"
    assert os.path.exists(expected_output_path)
    assert expected_output_path.read_text() == "### Complete Local Metadata Suite"

