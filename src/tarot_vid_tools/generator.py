#!/usr/bin/env python3
"""Tarot Video Tools: Dynamic lookups, size metrics, and auto-deck detection."""

import sys
import json
import urllib.request
import urllib.parse
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

    def load_all_cached_decks(self) -> List[DeckData]:
        """Scans the cache directory to load all existing deck models into memory."""
        decks = []
        for file_path in self.cache_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    decks.append(DeckData.from_dict(json.load(f)))
            except (json.JSONDecodeError, KeyError):
                continue
        return decks

class OpenLibraryDeckFetcher:
    """Queries open metadata frameworks to resolve sizes and names safely."""

    @staticmethod
    def _query_api(url: str) -> dict:
        headers = {"User-Agent": "tarot-vid-tools/0.1.0 (csuttles@case)"}
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception:  # pylint: disable=broad-except
            return {}

    def fetch_card_details(self, deck_name: str) -> Tuple[List[str], Optional[int]]:
        """Resolves deck assets and extracts actual card counts from descriptions."""
        import re

        encoded_name = urllib.parse.quote(deck_name)
        search_url = f"https://openlibrary.org{encoded_name}"
        search_data = self._query_api(search_url)

        docs = search_data.get("docs", [])
        if not docs or not isinstance(docs, list):
            return [], None

        inferred_count = None
        for doc in docs[:3]:
            for text_field in [doc.get("title", ""), " ".join(doc.get("text", []))]:
                match = re.search(
                    r"(\d+)[-\s]*(?:card|portal|gate)", text_field, re.IGNORECASE
                )
                if match:
                    inferred_count = int(match.group(1))
                    break

        if len(docs) == 0:
            return [], inferred_count

        target_doc = docs
        work_key = target_doc.get("key")
        if not work_key:
            return [], inferred_count

        work_data = self._query_api(f"https://openlibrary.org{work_key}.json")
        description = work_data.get("description", "")
        if isinstance(description, dict):
            description = description.get("value", "")

        if not inferred_count and description:
            match = re.search(
                r"(\d+)[-\s]*(?:card|portal|gate)", description, re.IGNORECASE
            )
            if match:
                inferred_count = int(match.group(1))

        lines = description.split("\n")
        card_names = []
        for line in lines:
            match = re.search(r"(?:-|\d+\.)\s*([A-Z][a-zA-Z\s]{3,30})", line)
            if match:
                card_names.append(match.group(1).strip())

        return sorted(list(set(card_names))), inferred_count


class SemanticAttributeEnricher:
    """Evaluates extracted tokens against matrices to infer metadata fields."""

    def __init__(self):
        # Comprehensive cross-reference multi-attribute blueprint configuration matrix layout
        self.matrix = [
            ("gateway", {
                "astrology": "Cosmic Gate / Galactic Node", "binary_yes_no": "Yes",
                "gender": "Non-Binary / Source", "element": "Cosmic Ether",
                "jungian": "Transcendent Function", "archetype": "The Portal",
                "cosmic": "Deep Space Portal", "energy": "High Frequency", "polarity": "Neutral"
            }),
            ("transmission", {
                "astrology": "Uranus / Fixed Star Decan", "binary_yes_no": "Yes",
                "gender": "Androgynous", "element": "Plasma / Light",
                "jungian": "Active Imagination", "archetype": "The Messenger",
                "cosmic": "Interstellar Wave", "energy": "Vibrational Upgrade", "polarity": "Active"
            }),
            ("chakra", {
                "astrology": "Inner Planet Alignment", "binary_yes_no": "Neutral",
                "gender": "Balanced", "element": "Prana Field",
                "jungian": "Self-Regulation", "archetype": "The Anchor",
                "cosmic": "Microcosmic Reflection", "energy": "Bio-Electric", "polarity": "Dual"
            }),
            ("temple", {
                "astrology": "Saturn / 4th House Home", "binary_yes_no": "Yes",
                "gender": "Feminine / Receptive", "element": "Earth Anchor",
                "jungian": "The Sanctuary / Temenos", "archetype": "The Hermit",
                "cosmic": "Ethereal Retreat Core", "energy": "Stabilized Power", "polarity": "Passive"
            }),
            ("wands", {
                "astrology": "Sun / Fire Mars Decan", "binary_yes_no": "Yes",
                "gender": "Masculine / Expressive", "element": "Fire",
                "jungian": "Libido / Psychic Drive", "archetype": "The Hero / Creator",
                "cosmic": "Solar Flare Core", "energy": "Dynamic / Kinetic", "polarity": "Positive"
            }),
            ("cups", {
                "astrology": "Moon / Venus Water Decan", "binary_yes_no": "Yes",
                "gender": "Feminine / Receptive", "element": "Water",
                "jungian": "Anima / Feeling Function", "archetype": "The Lover / Mystic",
                "cosmic": "Lunar Lunar Core", "energy": "Fluidic / Astral", "polarity": "Negative"
            }),
            ("swords", {
                "astrology": "Mercury / Saturn Air Decan", "binary_yes_no": "No",
                "gender": "Masculine / Direct", "element": "Air",
                "jungian": "Persona / Thinking Function", "archetype": "The Ruler / Sage",
                "cosmic": "Nebula Cloud Split", "energy": "Focused / Electric", "polarity": "Positive"
            }),
            ("pentacles", {
                "astrology": "Jupiter / Taurus Earth Decan", "binary_yes_no": "Yes",
                "gender": "Feminine / Grounded", "element": "Earth",
                "jungian": "Shadow / Sensation Function", "archetype": "The Provider",
                "cosmic": "Planetary Crust Gravity", "energy": "Magnetic / Dense", "polarity": "Negative"
            }),
            ("fool", {
                "astrology": "Uranus / Zero State Node", "binary_yes_no": "Yes",
                "gender": "Unmanifest Potency", "element": "Air / Æther",
                "jungian": "The Puer Aeternus Core", "archetype": "The Innocent / Wanderer",
                "cosmic": "Pre-Big-Bang Singularity", "energy": "Pure Potential", "polarity": "Neutral"
            })
        ]

    def enrich_card(self, card_name: str) -> Dict[str, str]:
        """Scans card naming structures to extrapolate taxonomy definitions dynamically."""
        lower_name = card_name.lower()
        for keyword, inferred_attrs in self.matrix:
            if keyword in lower_name:
                return inferred_attrs.copy()

        return {
            "astrology": "Universal Blueprint System", "binary_yes_no": "Neutral",
            "gender": "Unified Field Essence", "element": "Aura Field Synthesis",
            "jungian": "Collective Unconscious Space", "archetype": "The Shadow Prototype",
            "cosmic": "Nebula Grounding Matrix", "energy": "Radiant Vibration", "polarity": "Balanced"
        }

class OptimizedSlidingWindowAnalyzer:
    """Core analytical component evaluating timelines with reversal matching."""

    def __init__(
        self, base_window_size: int = 4, max_expanded_size: int = 12, step_size: int = 1
    ):
        self.base_window_size = base_window_size
        self.max_expanded_size = max_expanded_size
        self.step_size = step_size
        self.rev_keywords = {"reversed", "upside down", "inverted", "flipped"}

    def detect_active_decks(
        self, sub_file: pysrt.SubRipFile, all_decks: List[DeckData]
    ) -> List[DeckData]:
        """Scans raw dialogue to isolate decks that hit meaningful keyword matches."""
        full_text = " ".join([cue.text for cue in sub_file if hasattr(cue, "text")]).lower()
        matched_decks = []

        for deck in all_decks:
            match_count = sum(1 for card_key in deck.lookup_keys if card_key in full_text)
            if match_count >= 2:
                matched_decks.append(deck)
        return matched_decks

    def _scan_decks_for_match(
        self, text: str, decks: List[DeckData], kw_set: Set[str], seen: Set[Tuple[str, str]]
    ) -> List[Tuple[str, CardData, bool]]:
        matches = []
        if not any(kw in text for kw in kw_set):
            return matches

        for deck in decks:
            for card_key in deck.lookup_keys:
                if card_key in text and (deck.deck_name, card_key) not in seen:
                    is_rev = any(rw in text for rw in self.rev_keywords)
                    matches.append((deck.deck_name, deck.cards[card_key], is_rev))
                    seen.add((deck.deck_name, card_key))
        return matches

    def _expand_window_horizontally(
        self, sub_file: pysrt.SubRipFile, start_idx: int, decks: List[DeckData], seen: Set[Tuple[str, str]]
    ) -> Tuple[List[Tuple[str, CardData, bool]], int]:
        expanded_matches = []
        current_size = self.base_window_size
        total_cues = len(sub_file)

        while current_size < self.max_expanded_size and (start_idx + current_size) < total_cues:
            current_size += 1
            segment = sub_file[start_idx : start_idx + current_size]
            exp_text = " ".join([cue.text for cue in segment if hasattr(cue, "text")]).lower()

            found_new = False
            for deck in decks:
                for card_key in deck.lookup_keys:
                    if card_key in exp_text and (deck.deck_name, card_key) not in seen:
                        is_rev = any(rw in exp_text for rw in self.rev_keywords)
                        expanded_matches.append((deck.deck_name, deck.cards[card_key], is_rev))
                        seen.add((deck.deck_name, card_key))
                        found_new = True

            if not found_new and current_size > (self.base_window_size + 2):
                break
        return expanded_matches, current_size

    def _build_chapter_title(self, hits: List[Tuple[str, CardData, bool]]) -> str:
        card_strs = []
        for d_name, card, is_rev in hits:
            num_suffix = f" [{card.number}]" if card.number else ""
            rev_suffix = " (Reversed)" if is_rev else ""
            ast_val = card.attributes.get("astrology", "Universal")
            card_strs.append(f"[{d_name}] {card.name}{num_suffix}{rev_suffix} <{ast_val}>")
        return " + ".join(card_strs)

    def _get_cue_seconds(self, sub_time) -> int:
        return sub_time.hours * 3600 + sub_time.minutes * 60 + sub_time.seconds

    def _process_match(
        self,
        sub_file: pysrt.SubRipFile,
        idx: int,
        decks: List[DeckData],
        seen: Set[Tuple[str, str]],
        hits: List[Tuple[str, CardData, bool]],
    ) -> Tuple[str, int]:
        exp_hits, final_size = self._expand_window_horizontally(sub_file, idx, decks, seen)
        hits.extend(exp_hits)
        return self._build_chapter_title(hits), final_size

    def _append_or_merge_chapter(self, chapters: List[dict], start_sec: int, title: str) -> None:
        if chapters and (start_sec - self._time_to_seconds(chapters[-1]["timestamp"]) < 10):
            chapters[-1]["title"] += f" + {title}"
        else:
            chapters.append({"timestamp": self._seconds_to_time(start_sec), "title": title})

    def analyze_chapters(
        self, sub_file: pysrt.SubRipFile, decks: List[DeckData], keywords: List[str]
    ) -> List[dict]:
        """Analyzes subtitle timelines to generate chapter milestone tracks."""
        chapters = []
        seen_cards: Set[Tuple[str, str]] = set()
        kw_set = set(keywords)

        if sub_file and len(sub_file) > 0:
            intro_sec = self._get_cue_seconds(sub_file.start)
            chapters.append(
                {"timestamp": self._seconds_to_time(intro_sec), "title": "Introduction & Grounding"}
            )

        i, total_cues = 0, len(sub_file)
        while i < total_cues:
            window = sub_file[i : i + self.base_window_size]
            if not window or len(window) == 0:
                i += self.step_size
                continue

            window_text = " ".join([cue.text for cue in window if hasattr(cue, "text")]).lower()
            start_sec = self._get_cue_seconds(window.start)

            hits = self._scan_decks_for_match(window_text, decks, kw_set, seen_cards)
            if hits:
                title, final_size = self._process_match(sub_file, i, decks, seen_cards, hits)
                self._append_or_merge_chapter(chapters, start_sec, title)
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

# ==============================================================================
# CLI Group Definition (Must be defined first to resolve decorator references)
# ==============================================================================

@click.group()
def main():
    """Tarot Video Tools: Orchestrator managing dynamic chapter extraction metrics."""
    pass


# ==============================================================================
# CLI Subcommands
# ==============================================================================

@main.command()
@click.option("--name", required=True, type=str, help="Target identity designation code key.")
@click.option(
    "--type",
    "deck_type_arg",
    default="tarot",
    type=click.Choice(["tarot", "oracle"]),
    help="Deck structure template layout.",
)
@click.option("--cache-dir", default=".deck_cache", type=str, help="Pathway for cache operations.")
def bootstrap(name: str, deck_type_arg: str, cache_dir: str):
    """Auto-generates localized registries using specialized fallback sizing arrays."""
    repo = LocalDeckRepository(cache_dir)
    deck = DeckData(deck_name=name, deck_type=deck_type_arg)

    click.echo(f"Querying open directories to discover card assets for '{name}'...")
    fetcher = OpenLibraryDeckFetcher()
    enricher = SemanticAttributeEnricher()
    card_names, extracted_size = fetcher.fetch_card_details(name)

    if not card_names:
        low_name = name.lower()
        target_size = extracted_size if extracted_size else 44

        if "spirit animal" in low_name:
            target_size = 68
        elif "wisdom of the oracle" in low_name or "goddess power" in low_name:
            target_size = 52
        elif "postcards from spirit" in low_name or "moonology" in low_name:
            target_size = 52
        elif "crystal spirits" in low_name:
            target_size = 58
        elif "enchanted map" in low_name or "the map oracle" in low_name:
            target_size = 54
        elif "ancestors" in low_name:
            target_size = 55
        elif "starseed" in low_name:
            target_size = 53
        elif "7 energies" in low_name:
            target_size = 49
        elif "mystical shaman" in low_name or "shaman's dream" in low_name:
            target_size = 64
        elif "alchemy" in low_name:
            target_size = 71
        elif "animal spirit" in low_name:
            target_size = 63
        elif "keepers of the light" in low_name:
            target_size = 45

        if deck_type_arg == "tarot":
            majors = [
                "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
                "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
                "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
                "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement",
                "The World"
            ]
            card_names = majors
            for suit in ["Wands", "Cups", "Swords", "Pentacles"]:
                card_names.append(f"Ace of {suit}")
                card_names.extend([f"{n} of {suit}" for n in range(2, 11)])
                card_names.extend([f"{c} of {suit}" for c in ["Page", "Knight", "Queen", "King"]])
        else:
            card_names = [f"Oracle Key Card Entry {i}" for i in range(1, target_size + 1)]

    for idx, card_title in enumerate(card_names):
        inferred_attrs = enricher.enrich_card(card_title)
        deck.cards[card_title.lower().strip()] = CardData(
            name=card_title, number=str(idx + 1), attributes=inferred_attrs
        )

    repo.save_deck(deck)
    click.echo(f"Successfully serialized {len(deck.cards)} cards into local cache storage.")


@main.command()
@click.argument("srt_file", type=click.Path(exists=True))
@click.option(
    "--deck",
    "deck_list",
    multiple=True,
    required=False,
    help="Target validation registries. If blank, automatically scans speech dialogue.",
)
@click.option(
    "--cache-dir", default=".deck_cache", type=str, help="Workspace location configuration."
)
@click.option("--output", type=click.Path(), help="Target file layout destination file route.")
def parse(srt_file: str, deck_list: Tuple[str, ...], cache_dir: str, output: Optional[str]):
    """Analyzes physical subtitle tracks against registered lookup catalogs."""
    repo = LocalDeckRepository(cache_dir)
    sub_file = pysrt.open(srt_file, encoding="utf-8")
    analyzer = OptimizedSlidingWindowAnalyzer()

    if not deck_list:
        click.echo("No explicit decks provided. Scanning dialogue for keyword signatures...")
        all_cached_decks = repo.load_all_cached_decks()
        active_decks = analyzer.detect_active_decks(sub_file, all_cached_decks)
        if not active_decks:
            click.echo("Error: Unable to auto-detect any active deck cache templates.", err=True)
            sys.exit(1)
        discovered_names = [d.deck_name for d in active_decks]
        click.echo(f"Auto-detected active registries: {', '.join(discovered_names)}")
    else:
        active_decks = [repo.load_deck(name) for name in deck_list if repo.load_deck(name)]

    if not active_decks:
        click.echo("Error: Specified registries could not be resolved.", err=True)
        sys.exit(1)

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

