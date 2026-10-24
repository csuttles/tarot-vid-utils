#!/usr/bin/env python3
"""Tarot Video Tools: Dynamic lookups, deep metadata enrichment, and dense narrative tracking."""

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
from pysrt import SubRipFile, SubRipItem


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
            "astrology": "Mars / Aries Decan Axis", "binary_yes_no": "Neutral",
            "gender": "Unified Field Essence", "element": "Earth & Fire Synthesis",
            "jungian": "Collective Unconscious Space", "archetype": "The Shadow Prototype",
            "cosmic": "Nebula Grounding Matrix", "energy": "Radiant Vibration", "polarity": "Balanced"
        }

class OptimizedSlidingWindowAnalyzer:
    """Core analytical component transforming timeline hits into dense narrative sentences."""

    def __init__(
        self, base_window_size: int = 4, max_expanded_size: int = 12, step_size: int = 1
    ):
        self.base_window_size = base_window_size
        self.max_expanded_size = max_expanded_size
        self.step_size = step_size
        self.rev_keywords = {"reversed", "upside down", "inverted", "flipped"}

        # Mapping rich, detailed semantic associations directly onto framework keywords
        self.frameworks = [
            ("channeled message", ["channeled", "channeling", "download", "received transmission"],
             "A direct spiritual stream channeling higher intelligence down into conscious awareness."),
            ("psychic mediumship", ["mediumship", "psychic", "spirit world", "clairvoyant"],
             "Bridging the veil via clairvoyant senses to access multi-dimensional ancestral guidance."),
            ("jungian archetype", ["jungian", "archetype", "shadow self", "collective unconscious", "anima"],
             "Activating structural components of the collective subconscious to integrate split persona aspects."),
            ("qhht session", ["qhht", "quantum healing", "past life regression", "dolores cannon"],
             "Inducing deep somnambulistic trance states to pull somatic insights from past-life regressions."),
            ("reiki healing", ["reiki", "attunement", "life force energy"],
             "Channelling universal life force energy through palm positions to balance bio-field anomalies."),
            ("astrology alignment", ["astrology", "natal chart", "transit", "zodiac", "rising sign"],
             "Mapping active transits and hard planetary aspects interacting directly with geometric birth charts."),
            ("sound therapy", ["sound healing", "solfeggio", "binaural", "tuning fork"],
             "Utilizing solfeggio sound healing frequencies to alter brainwave states and drop somatic resistance."),
            ("shamanic practice", ["shaman", "mesa", "lower world", "soul retrieval"],
             "Engaging Andean shamanism techniques to clear heavy energy and anchor a localized medicine axis."),
            ("deity presence", ["hecate", "archangel michael", "lilith", "osiris", "isis"],
             "Invoking primordial cosmic currents through archetypal deities to anchor transmutational spaces.")
        ]

    def detect_active_decks(
        self, sub_file: SubRipFile, all_decks: List[DeckData]
    ) -> List[DeckData]:
        """Isolates active frameworks, enforcing strict hierarchical priority filters."""
        full_text = " ".join([cue.text for cue in sub_file if hasattr(cue, "text")]).lower()
        matched_tarot = []
        matched_oracle = []

        for deck in all_decks:
            match_count = sum(1 for card_key in deck.lookup_keys if card_key in full_text)
            if match_count >= 2:
                if deck.deck_type == "tarot":
                    matched_tarot.append(deck)
                else:
                    matched_oracle.append(deck)

        priority_order = ["rider waite", "golden dawn", "hermetic"]
        sorted_tarot = []

        for priority in priority_order:
            for deck in matched_tarot:
                if priority in deck.deck_name.lower() and deck not in sorted_tarot:
                    sorted_tarot.append(deck)

        for deck in matched_tarot:
            if deck not in sorted_tarot:
                sorted_tarot.append(deck)

        return sorted_tarot[:3] + matched_oracle

    def _scan_frameworks(self, text: str) -> List[str]:
        """Compiles dense contextual descriptions for active spiritual modalities spoken in window."""
        active_descriptions = []

        # Check specific transits or aspects if astrology terms are used
        if "astrology" in text or "transit" in text:
            aspect = "Conjunction" if "conjunction" in text else "Opposition" if "opposition" in text else "Transit Aspect"
            active_descriptions.append(f"Astrology ({aspect} involving current celestial movements).")

        # Process standard framework keywords
        for name, keywords, summary in self.frameworks:
            if any(kw in text for kw in keywords):
                if name == "jungian archetype":
                    # Interpolate explicit archetypes if mentioned explicitly
                    arch = "Hecate / Crone" if "hecate" in text else "The Shadow" if "shadow" in text else "Anima"
                    active_descriptions.append(f"Jungian Archetype (Integrating the {arch} dynamic into ego consciousness).")
                elif name == "deity presence":
                    deity = "Hecate" if "hecate" in text else "Lilith" if "lilith" in text else "Archangel Michael" if "michael" in text else "The Divine Entity"
                    active_descriptions.append(f"Deity Presence (Invoking {deity} to anchor and oversee transmutational workspace currents).")
                else:
                    active_descriptions.append(f"{name.title()} ({summary})")
        return active_descriptions

    def _scan_decks_for_match(
        self, text: str, decks: List[DeckData], kw_set: Set[str], seen_counts: Dict[Tuple[str, str], int]
    ) -> List[Tuple[str, CardData, bool]]:
        matches = []
        if not any(kw in text for kw in kw_set):
            return matches

        for deck in decks:
            for card_key in deck.lookup_keys:
                if card_key in text:
                    if seen_counts.get((deck.deck_name, card_key), 0) >= 3:
                        continue
                    is_rev = any(rw in text for rw in self.rev_keywords)
                    matches.append((deck.deck_name, deck.cards[card_key], is_rev))
                    seen_counts[(deck.deck_name, card_key)] = seen_counts.get((deck.deck_name, card_key), 0) + 1
        return matches

    def _expand_window_horizontally(
        self, sub_file: SubRipFile, start_idx: int, decks: List[DeckData], seen_counts: Dict[Tuple[str, str], int]
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
                    if card_key in exp_text:
                        if seen_counts.get((deck.deck_name, card_key), 0) >= 3:
                            continue
                        is_rev = any(rw in exp_text for rw in self.rev_keywords)
                        expanded_matches.append((deck.deck_name, deck.cards[card_key], is_rev))
                        seen_counts[(deck.deck_name, card_key)] = seen_counts.get((deck.deck_name, card_key), 0) + 1
                        found_new = True

            if not found_new and current_size > (self.base_window_size + 2):
                break
        return expanded_matches, current_size

    def _build_chapter_title(self, hits: List[Tuple[str, CardData, bool]], meta_topics: List[str]) -> str:
        narrative_parts = []

        # 1. Base Framework Topic Narratives
        if meta_topics:
            narrative_parts.append(" ".join(meta_topics))

        # 2. Rich, High-Density Card Narratives
        card_narratives = []
        for d_name, card, is_rev in hits:
            rev_str = " in reverse orientation" if is_rev else " in upright alignment"
            elem = card.attributes.get("element", "Aura Field")
            astro = card.attributes.get("astrology", "Universal")

            # Formulate full descriptive sentence pairing card art directly with core elements
            card_desc = (
                f"Activation of {card.name} ({d_name}){rev_str}, grounding structured archetypal "
                f"currents directly through the element of {elem} and corresponding {astro} attributes."
            )
            card_narratives.append(card_desc)

        if card_narratives:
            narrative_parts.append(" ".join(card_narratives))

        return " | ".join(narrative_parts)

    def _get_cue_seconds(self, sub_time) -> int:
        return sub_time.hours * 3600 + sub_time.minutes * 60 + sub_time.seconds

    def _process_match(
        self,
        sub_file: SubRipFile,
        idx: int,
        decks: List[DeckData],
        seen_counts: Dict[Tuple[str, str], int],
        hits: List[Tuple[str, CardData, bool]],
        meta_topics: List[str]
    ) -> Tuple[str, int]:
        exp_hits, final_size = self._expand_window_horizontally(sub_file, idx, decks, seen_counts)
        hits.extend(exp_hits)
        return self._build_chapter_title(hits, meta_topics), final_size

    def _append_or_merge_chapter(self, chapters: List[dict], start_sec: int, title: str) -> None:
        if chapters and (start_sec - self._time_to_seconds(chapters[-1]["timestamp"]) < 10):
            chapters[-1]["title"] += f" {title}"
        else:
            chapters.append({"timestamp": self._seconds_to_time(start_sec), "title": title})

    def analyze_chapters(
        self, sub_file: SubRipFile, decks: List[DeckData], keywords: List[str]
    ) -> List[dict]:
        """Analyzes subtitle timelines to generate chapter milestone tracks."""
        chapters = []
        seen_card_counts: Dict[Tuple[str, str], int] = {}
        kw_set = set(keywords)

        if sub_file and len(sub_file) > 0:
            intro_sec = self._get_cue_seconds(sub_file.start)

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

