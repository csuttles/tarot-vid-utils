"""Tarot Video Tools: Dynamic lookups, deep metadata enrichment, and dense narrative tracking."""

import sys
import json
import os
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
        return self._normalized_keys

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

    def load_all_cached_decks(self) -> List[DeckData]:
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
        except Exception:
            return {}

    def fetch_card_details(self, deck_name: str) -> Tuple[List[str], Optional[int]]:
        import re
        encoded_name = urllib.parse.quote(deck_name)
        search_url = f"https://openlibrary.org{encoded_name}"
        search_data = self._query_api(search_url)

        docs = search_data.get("docs", [])
        if not docs or not isinstance(docs, list):
            return [], None

        inferred_count = None
        for doc in docs[:3]:
            text_to_check = doc.get("title", "") + " " + " ".join(doc.get("text", []))
            match = re.search(r"(\d+)[-\s]*(?:card|portal|gate)", text_to_check, re.IGNORECASE)
            if match:
                inferred_count = int(match.group(1))
                break

        target_doc = docs[0]
        work_key = target_doc.get("key")
        if not work_key:
            return [], inferred_count

        work_data = self._query_api(f"https://openlibrary.org{work_key}.json")
        description = work_data.get("description", "")
        if isinstance(description, dict):
            description = description.get("value", "")

        if not inferred_count and description:
            match = re.search(r"(\d+)[-\s]*(?:card|portal|gate)", description, re.IGNORECASE)
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
            ("gateway", {"astrology": "Cosmic Gate / Galactic Node", "element": "Cosmic Ether"}),
            ("transmission", {"astrology": "Uranus / Fixed Star Decan", "element": "Plasma / Light"}),
            ("chakra", {"astrology": "Inner Planet Alignment", "element": "Prana Field"}),
            ("temple", {"astrology": "Saturn / 4th House Home", "element": "Earth Anchor"}),
            ("wands", {"astrology": "Sun / Fire Mars Decan", "element": "Fire"}),
            ("cups", {"astrology": "Moon / Venus Water Decan", "element": "Water"}),
            ("swords", {"astrology": "Mercury / Saturn Air Decan", "element": "Air"}),
            ("pentacles", {"astrology": "Jupiter / Taurus Earth Decan", "element": "Earth"}),
            ("fool", {"astrology": "Uranus / Zero State Node", "element": "Air / Æther"})
        ]

    def enrich_card(self, card_name: str) -> Dict[str, str]:
        lower_name = card_name.lower()
        for keyword, inferred_attrs in self.matrix:
            if keyword in lower_name:
                return inferred_attrs.copy()
        return {"astrology": "Mars / Aries Decan Axis", "element": "Earth & Fire Synthesis"}


class OptimizedSlidingWindowAnalyzer:
    """Core analytical component transforming timeline hits into dense unique sentences."""

    def __init__(self, base_window_size: int = 4, max_expanded_size: int = 12, step_size: int = 1):
        self.base_window_size = base_window_size
        self.max_expanded_size = max_expanded_size
        self.step_size = step_size
        self.rev_keywords = {"reversed", "upside down", "inverted", "flipped"}

        self.frameworks = [
            ("channeled message", ["channeled", "channeling", "download"], "Stream channeling higher intelligence."),
            ("psychic mediumship", ["mediumship", "psychic", "spirit world"], "Bridging the veil via clairvoyant senses."),
            ("jungian archetype", ["jungian", "archetype", "shadow self"], "Integrating structural subconscious modules."),
            ("qhht session", ["qhht", "quantum healing", "past life"], "Inducing deep somnambulistic trance states."),
            ("reiki healing", ["reiki", "attunement", "life force"], "Channelling universal life force energy through fields."),
            ("astrology alignment", ["astrology", "natal chart", "transit"], "Evaluating active cosmic transits."),
            ("sound therapy", ["sound healing", "solfeggio", "tuning fork"], "Utilizing sound frequencies to drop resistance."),
            ("shamanic practice", ["shaman", "mesa", "lower world"], "Engaging shamanic techniques to shift energy."),
            ("deity presence", ["hecate", "lilith", "osiris", "isis"], "Invoking primordial currents to anchor spaces.")
        ]

    @staticmethod
    def _recursive_rephrase(base_title: str, history: List[str], depth: int = 0) -> str:
        """Recursively alters titles to guarantee absolute unique phrasing variance on timelines."""
        if not history or base_title not in history or depth >= 3:
            return base_title

        # Phrase mutation variants bank
        rephrase_variants = {
            "Deity Presence": [
                "Deity Presence (Lilith deepens the transmutational current within the workspace field).",
                "Deity Presence (Lilith stabilizes active workspace energy loops).",
                "Deity Presence (Lilith reinforces workspace boundary integrity)."
            ],
            "Introduction & Grounding": [
                "Establishing Space & Baseline Frequency Anchoring.",
                "Opening Alignment & Sacred Grounding Sequence."
            ],
            "Astrology Alignment": [
                "Astrology Chart Integration (Evaluating active celestial transit nodes).",
                "Planetary Aspects (Integrating birth chart configurations against current movements)."
            ]
        }

        for key, mutations in rephrase_variants.items():
            if key in base_title:
                return OptimizedSlidingWindowAnalyzer._recursive_rephrase(mutations[depth % len(mutations)], history, depth + 1)

        if "Activation:" in base_title:
            mutated = base_title
            replacements = [("Activation:", "Integration:"), ("Currents.", "Gateways Realignment."), ("grounding", "anchoring")]
            for old, new in replacements:
                if old in mutated:
                    mutated = mutated.replace(old, new, 1)
                    break
            return OptimizedSlidingWindowAnalyzer._recursive_rephrase(mutated, history, depth + 1)

        return OptimizedSlidingWindowAnalyzer._recursive_rephrase(f"{base_title} (Continued Integration)", history, depth + 1)

    def detect_active_decks(self, sub_file: SubRipFile, all_decks: List[DeckData]) -> List[DeckData]:
        full_text = " ".join([cue.text for cue in sub_file if hasattr(cue, "text")]).lower()
        matched_tarot, matched_oracle = [], []

        for deck in all_decks:
            match_count = sum(1 for k in deck.lookup_keys if k.replace("the ", "").strip() in full_text and len(k) > 3)
            if match_count >= 1:
                if deck.deck_type == "tarot":
                    matched_tarot.append(deck)
                else:
                    matched_oracle.append(deck)

        priority_order = ["rider waite", "golden dawn", "hermetic"]
        sorted_tarot = []
        for p in priority_order:
            for d in matched_tarot:
                if p in d.deck_name.lower() and d not in sorted_tarot:
                    sorted_tarot.append(d)
        for d in matched_tarot:
            if d not in sorted_tarot:
                sorted_tarot.append(d)

        return sorted_tarot[:3] + matched_oracle

    def _scan_frameworks(self, text: str) -> List[str]:
        active_descriptions = []
        if "astrology" in text or "transit" in text:
            asp = "Conjunction" if "conjunction" in text else "Opposition" if "opposition" in text else "Transit Aspect"
            active_descriptions.append(f"Astrology Alignment ({asp} involving current celestial movements).")

        for name, keywords, summary in self.frameworks:
            if any(kw in text for kw in keywords):
                if name == "jungian archetype":
                    arch = "Hecate / Crone" if "hecate" in text else "The Shadow" if "shadow" in text else "Anima"
                    active_descriptions.append(f"Jungian Archetype (Integrating the {arch} dynamic into ego consciousness).")
                elif name == "deity presence":
                    deity = "Hecate" if "hecate" in text else "Lilith" if "lilith" in text else "Archangel Michael" if "michael" in text else "The Divine Entity"
                    active_descriptions.append(f"Deity Presence ({deity} anchors transmutational workspace currents).")
                else:
                    active_descriptions.append(f"{name.title()} ({summary})")
        return active_descriptions

    def _scan_decks_for_match(self, text: str, decks: List[DeckData], kw_set: Set[str], seen_counts: Dict[Tuple[str, str], int]) -> List[Tuple[str, CardData, bool]]:
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

    def _expand_window_horizontally(self, sub_file: SubRipFile, start_idx: int, decks: List[DeckData], seen_counts: Dict[Tuple[str, str], int]) -> Tuple[List[Tuple[str, CardData, bool]], int]:
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
        if meta_topics:
            narrative_parts.append(" ".join(sorted(list(set(meta_topics)))))
        card_to_decks: Dict[str, Tuple[CardData, bool, List[str]]] = {}
        for d_name, card, is_rev in hits:
            if card.name not in card_to_decks:
                card_to_decks[card.name] = (card, is_rev, [])
            card_to_decks[card.name][2].append(d_name)

        card_narratives = []
        for card_name, (card, is_rev, deck_names) in card_to_decks.items():
            rev_str = " (Reversed)" if is_rev else " (Upright)"
            elem = card.attributes.get("element", "Aura Field")
            astro = card.attributes.get("astrology", "Universal")
            card_narratives.append(f"Activation: {card_name}{rev_str} - {elem} & {astro} Currents.")
        if card_narratives:
            narrative_parts.append(" | ".join(card_narratives))
        return " | ".join(narrative_parts)

    def _get_cue_seconds(self, sub_time) -> int:
        return sub_time.hours * 3600 + sub_time.minutes * 60 + sub_time.seconds

    def _process_match(self, sub_file: SubRipFile, idx: int, decks: List[DeckData], seen_counts: Dict[Tuple[str, str], int], hits: List[Tuple[str, CardData, bool]], meta_topics: List[str]) -> Tuple[str, int]:
        exp_hits, final_size = self._expand_window_horizontally(sub_file, idx, decks, seen_counts)
        hits.extend(exp_hits)
        return self._build_chapter_title(hits, meta_topics), final_size

    def _append_or_merge_chapter(self, chapters: List[dict], start_sec: int, title: str) -> None:
        if chapters and (start_sec - self._time_to_seconds(chapters[-1]["timestamp"]) < 10):
            chapters[-1]["title"] += f" {title}"
        else:
            chapters.append({"timestamp": self._seconds_to_time(start_sec), "title": title})

    def analyze_chapters(self, sub_file: SubRipFile, decks: List[DeckData], keywords: List[str]) -> List[dict]:
        chapters, history = [], []
        seen_card_counts = {}
        kw_set = set(keywords)

        if sub_file and len(sub_file) > 0:
            intro_sec = self._get_cue_seconds(sub_file[0].start)
            intro_title = "Introduction & Grounding (Setting space and establishing baseline energy frequencies)."
            chapters.append({"timestamp": self._seconds_to_time(intro_sec), "title": intro_title})
            history.append(intro_title)

        i, total_cues = 0, len(sub_file)
        while i < total_cues:
            window = sub_file[i : i + self.base_window_size]
            if not window or len(window) == 0:
                i += self.step_size
                continue
            window_text = " ".join([cue.text for cue in window if hasattr(cue, "text")]).lower()
            start_sec = self._get_cue_seconds(window[0].start)
            meta_topics = self._scan_frameworks(window_text)
            hits = self._scan_decks_for_match(window_text, decks, kw_set, seen_card_counts)

            if hits or meta_topics:
                raw_title, final_size = self._process_match(sub_file, i, decks, seen_card_counts, hits, meta_topics)
                polished_title = self._recursive_rephrase(raw_title, history)
                self._append_or_merge_chapter(chapters, start_sec, polished_title)
                history.append(polished_title)
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
    pass


@main.command()
@click.option("--name", required=True, type=str)
@click.option("--type", "deck_type_arg", default="tarot", type=click.Choice(["tarot", "oracle"]))
@click.option("--cache-dir", default=".deck_cache", type=str)
def bootstrap(name: str, deck_type_arg: str, cache_dir: str):
    repo = LocalDeckRepository(cache_dir)
    deck = DeckData(deck_name=name, deck_type=deck_type_arg)
    fetcher, enricher = OpenLibraryDeckFetcher(), SemanticAttributeEnricher()
    card_names, _ = fetcher.fetch_card_details(name)

    if not card_names:
        if deck_type_arg == "tarot":
            card_names = ["The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"]
            for suit in ["Wands", "Cups", "Swords", "Pentacles"]:
                card_names.append(f"Ace of {suit}")
                card_names.extend([f"{n} of {suit}" for n in range(2, 11)])
                card_names.extend([f"{c} of {suit}" for c in ["Page", "Knight", "Queen", "King"]])
        else:
            card_names = [f"Oracle Key Card Entry {i}" for i in range(1, 45)]

    for idx, card_title in enumerate(card_names):
        deck.cards[card_title.lower().strip()] = CardData(name=card_title, number=str(idx + 1), attributes=enricher.enrich_card(card_title))
    repo.save_deck(deck)


@main.command()
@click.argument("srt_file", type=click.Path(exists=True))
@click.option("--deck", "deck_list", multiple=True, required=False)
@click.option("--cache-dir", default=".deck_cache", type=str)
@click.option("--output", type=click.Path())
def parse(srt_file: str, deck_list: Tuple[str, ...], cache_dir: str, output: Optional[str]):
    repo = LocalDeckRepository(cache_dir)
    sub_file = pysrt.open(srt_file, encoding="utf-8")
    analyzer = OptimizedSlidingWindowAnalyzer()

    if not deck_list:
        active_decks = analyzer.detect_active_decks(sub_file, repo.load_all_cached_decks())
    else:
        active_decks = [repo.load_deck(n) for n in deck_list if repo.load_deck(n)]

    if not active_decks:
        click.echo("Error: Registries missing.", err=True)
        sys.exit(1)

    keywords = ["pull", "drawn", "card", "reveal", "show", "reading", "layout"]
    chapters = analyzer.analyze_chapters(sub_file, active_decks, keywords)
    output_text = "\n".join([f"{ch['timestamp']} {ch['title']}" for ch in chapters])

    if output:
        with open(Path(output), "w", encoding="utf-8") as f:
            f.write(output_text + "\n")
    else:
        click.echo(output_text)


if __name__ == "__main__":
    main()

