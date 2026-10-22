#!/usr/bin/env python3
"""Tarot Video Tools: Context-aware YouTube milestones from SRT transcripts."""

import sys
import json
from pathlib import Path
from functools import lru_cache
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Set, Tuple

import click
import pysrt


@dataclass
class CardData:
    """Dataclass holding discrete identity attributes for an individual card."""

    name: str
    number: Optional[str] = None
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class DeckData:
    """Collection model containing structural profiles for a card deck."""

    deck_name: str
    deck_type: str
    cards: Dict[str, CardData] = field(default_factory=dict)
    _normalized_keys: Set[str] = field(default_factory=set, init=False, repr=False)

    def __post_init__(self):
        self._normalized_keys = set(self.cards.keys())

    @property
    def lookup_keys(self) -> Set[str]:
        """Provides a clean public property tracking lowercased card keys safely."""
        return self._normalized_keys

    def to_dict(self) -> dict:
        """Serializes internal dataclass contents down into primitive records."""
        return {
            "deck_name": self.deck_name,
            "deck_type": self.deck_type,
            "cards": {k: asdict(v) for k, v in self.cards.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DeckData":
        """Deserializes raw template dictionary data matrices back into classes."""
        deck = cls(deck_name=data["deck_name"], deck_type=data["deck_type"])
        for k, v in data.get("cards", {}).items():
            deck.cards[k.lower().strip()] = CardData(
                name=v["name"],
                number=v.get("number"),
                attributes=v.get("attributes", {}),
            )
        deck.__post_init__()
        return deck


class LocalDeckRepository:
    """Persistence file layer managing isolated cache file transactions."""

    def __init__(self, cache_dir: str = ".deck_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @lru_cache(maxsize=32)
    def _get_path(self, deck_name: str) -> Path:
        chars = [c if c.isalnum() or c in "-_" else "_" for c in deck_name.lower()]
        sanitized = "".join(chars)
        return self.cache_dir / f"{sanitized}.json"

    def save_deck(self, deck: DeckData) -> None:
        """Saves a deck instance layout out down into local cache file structures."""
        filepath = self._get_path(deck.deck_name)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(deck.to_dict(), f, indent=4, ensure_ascii=False)

    @lru_cache(maxsize=16)
    def load_deck(self, deck_name: str) -> Optional[DeckData]:
        """Loads a structured deck object map out from a local cache file."""
        filepath = self._get_path(deck_name)
        if not filepath.exists():
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return DeckData.from_dict(json.load(f))

class OptimizedSlidingWindowAnalyzer:
    """Core analytical component evaluating timelines using standard windows."""

    def __init__(self, base_window_size: int = 4, max_expanded_size: int = 12, step_size: int = 1):
        self.base_window_size = base_window_size
        self.max_expanded_size = max_expanded_size
        self.step_size = step_size

    def _scan_decks_for_match(
        self, text: str, decks: List[DeckData], kw_set: Set[str], seen: Set[Tuple[str, str]]
    ) -> List[Tuple[str, CardData]]:
        matches = []
        if not any(kw in text for kw in kw_set):
            return matches

        for deck in decks:
            for card_key in deck.lookup_keys:
                if card_key in text and (deck.deck_name, card_key) not in seen:
                    matches.append((deck.deck_name, deck.cards[card_key]))
                    seen.add((deck.deck_name, card_key))
        return matches

    def _expand_window_horizontally(
        self, sub_file: pysrt.SubFile, start_idx: int, decks: List[DeckData], seen: Set[Tuple[str, str]]
    ) -> Tuple[List[Tuple[str, CardData]], int]:
        expanded_matches = []
        current_size = self.base_window_size
        total_cues = len(sub_file)

        while current_size < self.max_expanded_size and (start_idx + current_size) < total_cues:
            current_size += 1
            segment = sub_file[start_idx : start_idx + current_size]
            exp_text = " ".join([cue.text for cue in segment]).lower()

            found_new = False
            for deck in decks:
                for card_key in deck.lookup_keys:
                    if card_key in exp_text and (deck.deck_name, card_key) not in seen:
                        expanded_matches.append((deck.deck_name, deck.cards[card_key]))
                        seen.add((deck.deck_name, card_key))
                        found_new = True

            if not found_new and current_size > (self.base_window_size + 2):
                break
        return expanded_matches, current_size

    def _build_chapter_title(self, hits: List[Tuple[str, CardData]]) -> str:
        card_strs = []
        for d_name, card in hits:
            num_suffix = f" [{card.number}]" if card.number else ""
            card_strs.append(f"[{d_name}] {card.name}{num_suffix}")
        return " + ".join(card_strs)

    def _get_cue_seconds(self, sub_time) -> int:
        return sub_time.hours * 3600 + sub_time.minutes * 60 + sub_time.seconds

    def _process_match(
        self,
        sub_file: pysrt.SubFile,
        idx: int,
        decks: List[DeckData],
        seen: Set[Tuple[str, str]],
        hits: List[Tuple[str, CardData]],
    ) -> Tuple[str, int]:
        """Helper to compute lookahead text elements outside core footprint."""
        exp_hits, final_size = self._expand_window_horizontally(sub_file, idx, decks, seen)
        hits.extend(exp_hits)
        return self._build_chapter_title(hits), final_size

    def analyze_chapters(self, sub_file: pysrt.SubFile, decks: List[DeckData], keywords: List[str]) -> List[dict]:
        """Analyzes subtitle timelines to generate chapter milestone tracks."""
        chapters = []
        seen_cards: Set[Tuple[str, str]] = set()
        kw_set = set(keywords)

        if sub_file:
            intro_sec = self._get_cue_seconds(sub_file.start)
            chapters.append(
                {"timestamp": self._seconds_to_time(intro_sec), "title": "Introduction & Grounding"}
            )

        i, total_cues = 0, len(sub_file)
        while i < total_cues:
            window = sub_file[i : i + self.base_window_size]
            if not window:
                i += self.step_size
                continue

            window_text = " ".join([cue.text for cue in window]).lower()
            start_sec = self._get_cue_seconds(window.start)

            hits = self._scan_decks_for_match(window_text, decks, kw_set, seen_cards)
            if hits:
                title, final_size = self._process_match(sub_file, i, decks, seen_cards, hits)
                diff = start_sec - self._time_to_seconds(chapters[-1]["timestamp"])
                if chapters and (diff < 10):
                    chapters[-1]["title"] += f" + {title}"
                else:
                    chapters.append({"timestamp": self._seconds_to_time(start_sec), "title": title})
                i += final_size
                continue

            i += self.step_size
        return chapters

    @staticmethod
    @lru_cache(maxsize=128)
    def _seconds_to_time(seconds: int) -> str:
        return f"{seconds // 3600:02d}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"

    @staticmethod
    @lru_cache(maxsize=128)
    def _time_to_seconds(time_str: str) -> int:
        h, m, s = map(int, time_str.split(":"))
        return h * 3600 + m * 60 + s

@click.group()
def main():
    """Tarot Video Tools: Orchestrator managing dynamic chapter extraction metrics."""


@main.command()
@click.option("--name", required=True, type=str, help="Target identity designation code key.")
@click.option(
    "--type",
    "deck_type_arg",
    default="tarot",
    type=click.Choice(["tarot", "oracle"]),
    help="Deck architecture model layout.",
)
@click.option("--cache-dir", default=".deck_cache", type=str, help="Pathway for cache operations.")
def bootstrap(name: str, deck_type_arg: str, cache_dir: str):
    """Auto-generates structured asset registries for retrieval lookup pipelines."""
    repo = LocalDeckRepository(cache_dir)
    deck = DeckData(deck_name=name, deck_type=deck_type_arg)

    if deck_type_arg == "tarot":
        majors = [
            "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
            "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
            "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
            "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement",
            "The World",
        ]
        for idx, card_name in enumerate(majors):
            deck.cards[card_name.lower()] = CardData(name=card_name, number=str(idx))

        for suit in ["Wands", "Cups", "Swords", "Pentacles"]:
            deck.cards[f"ace of {suit.lower()}"] = CardData(name=f"Ace of {suit}", number="1")
            for num in range(2, 11):
                deck.cards[f"{num} of {suit.lower()}"] = CardData(name=f"{num} of {suit}", number=str(num))
            for court in ["Page", "Knight", "Queen", "King"]:
                deck.cards[f"{court.lower()} of {suit.lower()}"] = CardData(name=f"{court} of {suit}")
    else:
        deck.cards["placeholder card template"] = CardData(
            name="Template Card Name", number="1", attributes={"theme": "Universal"}
        )

    repo.save_deck(deck)
    click.echo(f"Successfully generated structured {deck_type_arg} template for '{name}'.")


@main.command()
@click.argument("srt_file", type=click.Path(exists=True))
@click.option(
    "--deck",
    "deck_list",
    multiple=True,
    required=True,
    help="Target validation registries lookup identifiers.",
)
@click.option(
    "--cache-dir", default=".deck_cache", type=str, help="Workspace location configuration."
)
@click.option("--output", type=click.Path(), help="Target file layout destination file route.")
def parse(srt_file: str, deck_list: Tuple[str, ...], cache_dir: str, output: Optional[str]):
    """Analyzes physical subtitle tracks against registered lookup catalogs."""
    repo = LocalDeckRepository(cache_dir)
    active_decks = [repo.load_deck(name) for name in deck_list if repo.load_deck(name)]

    if not active_decks:
        click.echo("Error: Specified registries could not be resolved.", err=True)
        sys.exit(1)

    sub_file = pysrt.open(srt_file, encoding="utf-8")
    analyzer = OptimizedSlidingWindowAnalyzer()
    keywords = [
        "pull", "drawn", "card", "reveal", "show", "position", "reading", "layout",
        "next", "coming through", "clarify",
    ]

    chapters = analyzer.analyze_chapters(sub_file, active_decks, keywords)
    output_lines = [f"{ch['timestamp']} {ch['title']}" for ch in chapters]
    output_text = "\n".join(output_lines)

    if output:
        with open(Path(output), "w", encoding="utf-8") as f:
            f.write(output_text + "\n")
        click.echo(f"Successfully compiled chapters down to '{output}'.")
    else:
        click.echo(output_text)


if __name__ == "__main__":
    main()


