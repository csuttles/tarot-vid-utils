#!/usr/bin/env python3
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
    name: str
    number: Optional[str] = None
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class DeckData:
    deck_name: str
    deck_type: str
    cards: Dict[str, CardData] = field(default_factory=dict)
    _normalized_keys: Set[str] = field(default_factory=set, init=False, repr=False)

    def __post_init__(self):
        self._normalized_keys = set(self.cards.keys())

    def to_dict(self) -> dict:
        return {
            "deck_name": self.deck_name,
            "deck_type": self.deck_type,
            "cards": {k: asdict(v) for k, v in self.cards.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DeckData":
        deck = cls(deck_name=data["deck_name"], deck_type=data["deck_type"])
        for k, v in data.get("cards", {}).items():
            deck.cards[k.lower().strip()] = CardData(
                name=v["name"], number=v.get("number"), attributes=v.get("attributes", {})
            )
        deck.__post_init__()
        return deck


class LocalDeckRepository:
    def __init__(self, cache_dir: str = ".deck_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @lru_cache(maxsize=32)
    def _get_path(self, deck_name: str) -> Path:
        sanitized = "".join(c if c.isalnum() or c in "-_" else "_" for c in deck_name.lower())
        return self.cache_dir / f"{sanitized}.json"

    def save_deck(self, deck: DeckData) -> None:
        filepath = self._get_path(deck.deck_name)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(deck.to_dict(), f, indent=4, ensure_ascii=False)

    @lru_cache(maxsize=16)
    def load_deck(self, deck_name: str) -> Optional[DeckData]:
        filepath = self._get_path(deck_name)
        if not filepath.exists():
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return DeckData.from_dict(json.load(f))


class OptimizedSlidingWindowAnalyzer:
    def __init__(self, base_window_size: int = 4, max_expanded_size: int = 12, step_size: int = 1):
        self.base_window_size = base_window_size
        self.max_expanded_size = max_expanded_size
        self.step_size = step_size

    def analyze_chapters(
        self, sub_file: pysrt.SubFile, decks: List[DeckData], contextual_keywords: List[str]
    ) -> List[dict]:
        chapters = []
        seen_cards: Set[Tuple[str, str]] = set()
        kw_set = set(contextual_keywords)

        if sub_file:
            first_cue = sub_file[0]
            intro_seconds = first_cue.start.hours * 3600 + first_cue.start.minutes * 60 + first_cue.start.seconds
            chapters.append({"timestamp": self._seconds_to_time(intro_seconds), "title": "Introduction & Grounding"})

        i = 0
        total_cues = len(sub_file)

        while i < total_cues:
            current_window_size = self.base_window_size
            window = sub_file[i : i + current_window_size]
            window_text = " ".join([cue.text for cue in window]).lower()

            if not window:
                i += self.step_size
                continue

            start_cue = window[0].start
            window_start_sec = start_cue.hours * 3600 + start_cue.minutes * 60 + start_cue.seconds
            detected_cards_in_window = []

            for deck in decks:
                for card_key in deck._normalized_keys:
                    if card_key in window_text and (deck.deck_name, card_key) not in seen_cards:
                        if any(kw in window_text for kw in kw_set):
                            detected_cards_in_window.append((deck.deck_name, deck.cards[card_key]))
                            seen_cards.add((deck.deck_name, card_key))

            if detected_cards_in_window:
                while current_window_size < self.max_expanded_size and (i + current_window_size) < total_cues:
                    current_window_size += 1
                    expanded_window = sub_file[i : i + current_window_size]
                    expanded_text = " ".join([cue.text for cue in expanded_window]).lower()

                    found_additional = False
                    for deck in decks:
                        for card_key in deck._normalized_keys:
                            if card_key in expanded_text and (deck.deck_name, card_key) not in seen_cards:
                                detected_cards_in_window.append((deck.deck_name, deck.cards[card_key]))
                                seen_cards.add((deck.deck_name, card_key))
                                found_additional = True

                    if not found_additional and current_window_size > (self.base_window_size + 2):
                        break

                card_strings = []
                for deck_name, card in detected_cards_in_window:
                    num_str = f" [{card.number}]" if card.number else ""
                    card_strings.append(f"[{deck_name}] {card.name}{num_str}")

                title = " + ".join(card_strings)

                if len(chapters) > 1 and (window_start_sec - self._time_to_seconds(chapters[-1]["timestamp"]) < 10):
                    chapters[-1]["title"] += f" + {title}"
                else:
                    chapters.append({"timestamp": self._seconds_to_time(window_start_sec), "title": title})

                i += current_window_size
                continue

            i += self.step_size

        return chapters

    @staticmethod
    @lru_cache(maxsize=128)
    def _seconds_to_time(seconds: int) -> str:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    @staticmethod
    @lru_cache(maxsize=128)
    def _time_to_seconds(time_str: str) -> int:
        h, m, s = map(int, time_str.split(":"))
        return h * 3600 + m * 60 + s


@click.group()
def main():
    """Tarot Video Tools: System orchestrator managing dynamic chapter extraction metrics."""
    pass


@main.command()
@click.option("--name", required=True, type=str, help="Target identity designation key for the deck file layout.")
@click.option(
    "--type", default="tarot", type=click.Choice(["tarot", "oracle"]), help="System architecture mapping model."
)
@click.option("--cache-dir", default=".deck_cache", type=str, help="Storage pathway routing for cache operations.")
def bootstrap(name: str, type: str, cache_dir: str):
    """Auto-generates comprehensive localized baseline asset registries for lookup extraction pipelines."""
    repo = LocalDeckRepository(cache_dir)
    deck = DeckData(deck_name=name, deck_type=type)

    if type == "tarot":
        majors = [
            "The Fool",
            "The Magician",
            "The High Priestess",
            "The Empress",
            "The Emperor",
            "The Hierophant",
            "The Lovers",
            "The Chariot",
            "Strength",
            "The Hermit",
            "Wheel of Fortune",
            "Justice",
            "The Hanged Man",
            "Death",
            "Temperance",
            "The Devil",
            "The Tower",
            "The Star",
            "The Moon",
            "The Sun",
            "Judgement",
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
    click.echo(f"Successfully generated structured {type} asset registry template under target key name '{name}'.")


@main.command()
@click.argument("srt_file", type=click.Path(exists=True))
@click.option(
    "--decks", nargs="+", required=True, help="Space-separated system validation registry lookup identifiers."
)
@click.option("--cache-dir", default=".deck_cache", type=str, help="Workspace location path for storage retrieval.")
@click.option("--output", type=click.Path(), help="Target file layout destination.")
def parse(srt_file: str, decks: List[str], cache_dir: str, output: Optional[str]):
    """Analyzes physical subtitle tracks against registered lookup catalogs to compute video chapters."""
    repo = LocalDeckRepository(cache_dir)
    active_decks = [repo.load_deck(name) for name in decks if repo.load_deck(name)]

    if not active_decks:
        click.echo("Error: Specified asset registries could not be resolved out of local caching volumes.", err=True)
        sys.exit(1)

    sub_file = pysrt.open(srt_file, encoding="utf-8")
    analyzer = OptimizedSlidingWindowAnalyzer()
    keywords = [
        "pull",
        "drawn",
        "card",
        "reveal",
        "show",
        "position",
        "reading",
        "layout",
        "next",
        "coming through",
        "clarify",
    ]

    chapters = analyzer.analyze_chapters(sub_file, active_decks, keywords)
    output_lines = [f"{ch['timestamp']} {ch['title']}" for ch in chapters]
    output_text = "\n".join(output_lines)

    if output:
        with open(Path(output), "w", encoding="utf-8") as f:
            f.write(output_text + "\n")
        click.echo(f"Successfully compiled {len(chapters)} operational chapters out down to '{output}'.")
    else:
        click.echo(output_text)


if __name__ == "__main__":
    main()
