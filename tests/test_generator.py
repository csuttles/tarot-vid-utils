"""Automated unit test suite verifying scanning logic and lookahead states."""

# pylint: disable=redefined-outer-name

import tempfile
from pathlib import Path
import pytest
import pysrt
from tarot_vid_tools.generator import (
    CardData,
    DeckData,
    LocalDeckRepository,
    OptimizedSlidingWindowAnalyzer,
)


@pytest.fixture
def sample_deck():
    """Generates a populated mock deck structure for tracking identification."""
    deck = DeckData(deck_name="Rider_Waite", deck_type="tarot")
    deck.cards["the fool"] = CardData(name="The Fool", number="0")
    deck.cards["the magician"] = CardData(name="The Magician", number="1")
    deck.cards["the high priestess"] = CardData(name="The High Priestess", number="2")
    deck.__post_init__()
    return deck


@pytest.fixture
def mock_srt_file():
    """Generates a temporary physical .srt file containing tracking metrics."""
    srt_content = (
        "1\n"
        "00:00:01,000 --> 00:00:04,000\n"
        "Welcome back. Today we are doing a fresh layout reading.\n\n"
        "2\n"
        "00:00:05,000 --> 00:00:09,000\n"
        "Let's look at the first card here. I pull the fool.\n\n"
        "3\n"
        "00:00:10,000 --> 00:00:14,000\n"
        "This is fascinating because right next to it, I reveal the magician too.\n"
    )
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".srt", delete=False, encoding="utf-8"
    ) as temp_file:
        temp_file.write(srt_content)
        temp_file_path = temp_file.name

    yield temp_file_path
    Path(temp_file_path).unlink()


def test_local_deck_repository_cache():
    """Verifies repository disk serialization works correctly in isolation."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo = LocalDeckRepository(cache_dir=tmp_dir)
        deck = DeckData(deck_name="Test_Oracle", deck_type="oracle")
        deck.cards["destiny"] = CardData(name="Destiny", number="44")
        deck.__post_init__()

        repo.save_deck(deck)
        loaded = repo.load_deck("Test_Oracle")

        assert loaded is not None
        assert loaded.deck_name == "Test_Oracle"
        assert "destiny" in loaded.lookup_keys
        assert loaded.cards["destiny"].number == "44"


def test_sliding_window_card_detection(mock_srt_file, sample_deck):
    """Verifies that individual window slices cross-reference keywords."""
    sub_file = pysrt.open(mock_srt_file, encoding="utf-8")
    analyzer = OptimizedSlidingWindowAnalyzer(base_window_size=2, step_size=1)
    keywords = ["pull", "reveal", "drawn"]

    chapters = analyzer.analyze_chapters(sub_file, [sample_deck], keywords)

    assert len(chapters) >= 2
    assert chapters[0]["title"] == "Introduction & Grounding"
    assert "The Fool" in chapters[1]["title"]


def test_dynamic_lookahead_expansion(sample_deck):
    """Ensures window size balloons when multiple tokens hit concurrently."""
    sub_file = pysrt.SubRipFile()

    cue1 = pysrt.SubRipItem(index=1, text="I pull the fool right here on the table.")
    cue1.start.seconds = 5

    cue2 = pysrt.SubRipItem(index=2, text="And look at this, we instantly reveal the magician.")
    cue2.start.seconds = 8

    cue3 = pysrt.SubRipItem(index=3, text="And even the high priestess arrives right behind.")
    cue3.start.seconds = 12

    sub_file.append(cue1)
    sub_file.append(cue2)
    sub_file.append(cue3)

    analyzer = OptimizedSlidingWindowAnalyzer(base_window_size=1, max_expanded_size=5, step_size=1)
    keywords = ["pull", "reveal"]

    chapters = analyzer.analyze_chapters(sub_file, [sample_deck], keywords)

    assert len(chapters) == 2
    assert "The Fool" in chapters[1]["title"]
    assert "The Magician" in chapters[1]["title"]

