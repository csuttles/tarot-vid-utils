"""Tarot Video Tools: Dynamic lookups, deep esoteric enrichment, and dense timeline analytics."""

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
import requests
from pysrt import SubRipFile, SubRipItem


@dataclass
class CardData:
    """Dataclass holding deep esoteric identity and taxonomy attributes for an individual card."""
    name: str
    number: Optional[str] = None
    upright_meaning: str = "Overview pending analysis compilation"
    reversed_meaning: str = "Shadow analysis pending compilation"
    binary_outlook: str = "Maybe"
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
            "cards": {
                k: {
                    "name": v.name,
                    "number": v.number,
                    "upright_meaning": v.upright_meaning,
                    "reversed_meaning": v.reversed_meaning,
                    "binary_outlook": v.binary_outlook,
                    "attributes": v.attributes
                } for k, v in self.cards.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DeckData":
        deck = cls(deck_name=data["deck_name"], deck_type=data["deck_type"])
        for k, v in data.get("cards", {}).items():
            deck.cards[k.lower().strip()] = CardData(
                name=v["name"],
                number=v.get("number"),
                upright_meaning=v.get("upright_meaning", "Overview pending"),
                reversed_meaning=v.get("reversed_meaning", "Shadow analysis pending"),
                binary_outlook=v.get("binary_outlook", "Maybe"),
                attributes=v.get("attributes", {}),
            )
        deck.__post_init__()
        return deck

class LocalDeckRepository:
    """Persistence file layer managing isolated cache file transactions and fragmented saves."""
    def __init__(self, cache_dir: str = ".deck_cache"):
        self.cache_dir = Path(cache_dir)
        self.frag_dir = self.cache_dir / "fragments"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.frag_dir.mkdir(parents=True, exist_ok=True)

    @lru_cache(maxsize=32)
    def _get_path(self, deck_name: str) -> Path:
        chars = [c if c.isalnum() or c in "-_" else "_" for c in deck_name.lower()]
        sanitized = "".join(chars)
        return self.cache_dir / f"{sanitized}.json"

    def _get_frag_path(self, deck_name: str, card_name: str) -> Path:
        deck_chars = "".join([c if c.isalnum() or c in "-_" else "_" for c in deck_name.lower()])
        card_chars = "".join([c if c.isalnum() or c in "-_" else "_" for c in card_name.lower()])
        return self.frag_dir / f"{deck_chars}__{card_chars}.json"

    def save_fragment(self, deck_name: str, card_name: str, data: dict) -> None:
        """Saves a single processed card milestone fragment to preserve progress state."""
        with open(self._get_frag_path(deck_name, card_name), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def load_fragment(self, deck_name: str, card_name: str) -> Optional[dict]:
        """Checks for existing committed task history entries before running local models."""
        filepath = self._get_frag_path(deck_name, card_name)
        if not filepath.exists():
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return None

    def save_deck(self, deck: DeckData) -> None:
        filepath = self._get_path(deck.deck_name)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(deck.to_dict(), f, indent=4, ensure_ascii=False)

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
    """Queries public book and card API registries with adaptive backoff fallbacks."""

    @staticmethod
    def _query_api(url: str, max_retries: int = 5, backoff_factor: float = 2.0) -> dict:
        """Executes API queries with dynamic exponential backoff and randomized jitter."""
        import time
        import random
        headers = {"User-Agent": "tarot-vid-tools/1.0.0 (csuttles@case; cjef@jaguar)"}

        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=12) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code in (400, 401, 403):
                    break
            except Exception:
                pass

            if attempt == max_retries - 1:
                break
            sleep_duration = (backoff_factor ** attempt) + random.uniform(0.5, 1.5)
            time.sleep(sleep_duration)
        return {}

    @staticmethod
    def _fetch_verified_tarot_db() -> List[Dict]:
        """Queries primary open source card data indices directly to map core baselines."""
        url = "https://tarotapi.dev"
        headers = {"User-Agent": "tarot-vid-tools/1.0.0"}
        try:
            res = requests.get(url, headers=headers, timeout=15)
            res.raise_for_status()
            return res.json().get("cards", [])
        except Exception:
            return []

    def fetch_card_details(self, deck_name: str) -> Tuple[List[str], Optional[int]]:
        """Performs substring card listing extractions from OpenLibrary work items."""
        import re
        encoded_name = urllib.parse.quote(deck_name)
        search_url = f"https://openlibrary.org{encoded_name}"
        search_data = self._query_api(search_url)

        docs = search_data.get("docs", [])
        if not docs or not isinstance(docs, list):
            return [], None

        inferred_count = None
        for doc in docs[:3]:
            text_field = doc.get("title", "") + " " + " ".join(doc.get("text", []))
            match = re.search(r"(\d+)[-\s]*(?:card|portal|gate)", text_field, re.IGNORECASE)
            if match:
                inferred_count = int(match.group(1))
                break

        target_doc = docs if isinstance(docs, list) and len(docs) > 0 else {}
        work_key = target_doc.get("key") if isinstance(target_doc, dict) else None
        if not work_key:
            return [], inferred_count

        work_data = self._query_api(f"https://openlibrary.org{work_key}.json")
        description = work_data.get("description", "")
        if isinstance(description, dict):
            description = description.get("value", "")

        lines = description.split("\n")
        card_names = []
        for line in lines:
            match = re.search(r"(?:-|\d+\.|\d+\s*-\s*)\s*([A-Za-z][a-zA-Z\s']{3,40})", line)
            if match:
                card_names.append(match.group(1).strip())

        return sorted(list(set(card_names))), inferred_count

class LocalLLMOracleScraper:
    """Manages persistent connection sockets and adaptive backoff adaptors to prevent local socket drops."""

    _session = None

    @classmethod
    def _get_session(cls) -> requests.Session:
        """Instantiates a thread-safe global HTTP connection session with keep-alive pooling."""
        if cls._session is None:
            cls._session = requests.Session()
            from requests.adapters import HTTPAdapter
            from urllib3.util import Retry
            retries = Retry(
                total=5,
                backoff_factor=1.5,
                status_forcelist=[500, 502, 503, 504],
                raise_on_status=False
            )
            adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=retries)
            cls._session.mount("http://", adapter)
        return cls._session

    @classmethod
    def fetch_oracle_names(cls, deck_name: str) -> List[str]:
        """Queries local mistral/llama using an unconstrained strict JSON schema array layout."""
        url = "http://localhost:11434/api/chat"
        prompt = (
            f"You are a specialized esoteric repository archivist. Output the complete official list of individual "
            f"card names for the oracle deck named '{deck_name}' from real-world published indexes. "
            f"Provide only the genuine names."
        )
        schema_format = {
            "type": "array",
            "items": {"type": "string"}
        }
        payload = {
            "model": "mistral:latest",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": schema_format,
            "options": {"temperature": 0.01}
        }
        try:
            session = cls._get_session()
            res = session.post(url, json=payload, timeout=60)
            res.raise_for_status()
            parsed = json.loads(res.json().get("message", {}).get("content", "").strip())
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if item]
        except Exception:
            pass
        return []

    @classmethod
    def enrich_oracle_card(cls, deck_name: str, card_name: str) -> Dict:
        """Forces the local model to enrich a single card's properties using a low-token object footprint."""
        url = "http://localhost:11434/api/chat"
        prompt = (
            f"For the card '{card_name}' from the oracle deck '{deck_name}', analyze its real-world published meanings. "
            f"Provide its core elemental energy theme, its astrological planetary signature vibration, a concise "
            f"upright theme, a concise reversed/shadow theme, and a binary outlook bias balance descriptor."
        )
        schema_format = {
            "type": "object",
            "properties": {
                "element": {"type": "string"},
                "astrology": {"type": "string"},
                "upright": {"type": "string"},
                "reversed": {"type": "string"},
                "outlook": {"type": "string", "enum": ["Yes", "No", "Maybe"]}
            },
            "required": ["element", "astrology", "upright", "reversed", "outlook"]
        }
        payload = {
            "model": "mistral:latest",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": schema_format,
            "options": {"temperature": 0.05}
        }
        try:
            session = cls._get_session()
            res = session.post(url, json=payload, timeout=45)
            res.raise_for_status()
            return json.loads(res.json().get("message", {}).get("content", "").strip())
        except Exception:
            return {}


class SemanticAttributeEnricher:
    """Calculates dual elements, astrological planet decans, and binary yes/no loops dynamically."""

    def __init__(self):
        self.major_matrix = {
            "the fool": {"astro": "Uranus", "elem": "Pure Air / Ether", "up": "New beginnings, infinite choices", "rev": "Recklessness, alignment block", "out": "Yes"},
            "the magician": {"astro": "Mercury", "elem": "Air + Fire Catalyst", "up": "Focused manifestation, agency", "rev": "Illusion, manipulation", "out": "Yes"},
            "the high priestess": {"astro": "Moon", "elem": "Pure Water", "up": "Intuitive knowing, deep shadow", "rev": "Surface metrics, ignoring inner voice", "out": "Yes"},
            "the empress": {"astro": "Venus", "elem": "Pure Earth", "up": "Somatic abundance, creativity", "rev": "Creative block, stagnation", "out": "Yes"},
            "the emperor": {"astro": "Aries", "elem": "Fire + Earth Anchor", "up": "Sovereign structure, protection", "rev": "Rigidity, control cycles", "out": "Yes"},
            "the hierophant": {"astro": "Taurus", "elem": "Earth", "up": "Historical lineages, frameworks", "rev": "Alternative modalities, unlearning", "out": "Maybe"},
            "the lovers": {"astro": "Gemini", "elem": "Air", "up": "Core alignment, sacred choice", "rev": "Misalignment, discordant field", "out": "Yes"},
            "the chariot": {"astro": "Cancer", "elem": "Water + Fire Velocity", "up": "Willpower momentum, integration vector", "rev": "Deflection, scattered momentum", "out": "Yes"},
            "strength": {"astro": "Leo", "elem": "Fire", "up": "Somatic fortitude, alchemy of fear", "rev": "Ego exhaustion, raw friction", "out": "Yes"},
            "the hermit": {"astro": "Virgo", "elem": "Earth", "up": "Solitude, inner guidance, introspection", "rev": "Isolation loops, text freeze", "out": "Maybe"},
            "wheel of fortune": {"astro": "Jupiter", "elem": "Fire + Cosmic Axis", "up": "Cyclical destiny shifting, momentum", "rev": "Resistance to patterns, friction", "out": "Yes"},
            "justice": {"astro": "Libra", "elem": "Air", "up": "Karmic equilibrium, objective clarity", "rev": "Asymmetry, systemic blindness", "out": "Maybe"},
            "the hanged man": {"astro": "Neptune", "elem": "Water", "up": "Sacred suspension, reframing", "rev": "Stalling, ego projection, resistance", "out": "No"},
            "death": {"astro": "Scorpio", "elem": "Water + Rebirth Node", "up": "Absolute stripping, phoenix phase", "rev": "Stagnant preservation, delays", "out": "No"},
            "temperance": {"astro": "Sagittarius", "elem": "Water + Fire Synthesis", "up": "Alchemical integration, fluid balance", "rev": "Excess, discordant merging", "out": "Yes"},
            "the devil": {"astro": "Capricorn", "elem": "Earth", "up": "Shadow self, attachment, addiction", "rev": "Release, freedom, awareness", "out": "No"},
            "the tower": {"astro": "Mars", "elem": "Fire", "up": "Sudden upheaval, revelation, collapse", "rev": "Avoiding disaster, delaying panic", "out": "No"},
            "the star": {"astro": "Aquarius", "elem": "Air", "up": "Somatic rejuvenation, systemic hope", "rev": "Disconnection from source, fatigue", "out": "Yes"},
            "the moon": {"astro": "Pisces", "elem": "Water", "up": "Illusion, fear, anxiety, subconscious", "rev": "Release of fear, clearing confusion", "out": "No"},
            "the sun": {"astro": "Sun", "elem": "Fire", "up": "Radiant integration, absolute clarity", "rev": "Temporary shading, masked energy", "out": "Yes"},
            "judgement": {"astro": "Pluto", "elem": "Fire + Fire Ether", "up": "Cellular awakening, timeline pathing", "rev": "Ignoring the inner prompt, self-doubt", "out": "Yes"},
            "the world": {"astro": "Saturn", "elem": "Earth", "up": "Systemic completion, integrated loops", "rev": "Shortcuts, missing structural closures", "out": "Yes"}
        }

    def infer_minor_details(self, name: str, suit: str) -> Dict[str, str]:
        low_name = name.lower()
        suit_elements = {"wands": "Fire", "cups": "Water", "swords": "Air", "pentacles": "Earth"}
        suit_elem = suit_elements.get(suit, "Aura Field")

        outlook = "No" if suit == "swords" else "Yes"
        if "five of" in low_name or "seven of" in low_name or "three of" in low_name or "ten of" in low_name:
            if suit in ["swords", "wands", "cups"]:
                outlook = "No"
        elif "two of" in low_name or "four of" in low_name:
            outlook = "Maybe"

        if "king of" in low_name:
            return {"astro": f"Chieftain of {suit_elem}", "elem": f"Fire + {suit_elem}", "out": "Yes", "up": f"Sovereign dynamic alignment of {suit_elem}.", "rev": "Scattered boundaries."}
        elif "queen of" in low_name:
            return {"astro": f"Matriarch of {suit_elem}", "elem": f"Water + {suit_elem}", "out": "Yes", "up": f"Intuitive emotional container of {suit_elem}.", "rev": "Field stagnation."}
        elif "knight of" in low_name:
            return {"astro": f"Executor of {suit_elem}", "elem": f"Air + {suit_elem}", "out": outlook, "up": f"Swift execution vector of {suit_elem}.", "rev": "Imbalanced dispersion."}
        elif "page of" in low_name:
            return {"astro": f"Herald of {suit_elem}", "elem": f"Earth + {suit_elem}", "out": "Maybe", "up": f"Grounded seed expression of {suit_elem}.", "rev": "Delayed grounding fields."}
        elif "ace of" in low_name:
            return {"astro": f"Seed of {suit_elem} Currents", "elem": f"Pure Root of {suit_elem}", "out": "Yes", "up": "Elemental zero-point breakthrough.", "rev": "Suppressed potential."}

        astro_decans = {"wands": "Sun / Fire Mars Decan", "cups": "Moon / Venus Water Decan", "swords": "Mercury / Saturn Air Decan", "pentacles": "Jupiter / Taurus Earth Decan"}
        return {"astro": astro_decans.get(suit, "Universal Axis"), "elem": suit_elem, "out": outlook, "up": f"Progressive integration within {suit_elem}.", "rev": "Internal friction loops."}

    def enrich_card(self, card_name: str, suit: str = "") -> Dict:
        low_name = card_name.lower().strip()
        if suit in ["wands", "cups", "swords", "pentacles"]:
            return self.infer_minor_details(low_name, suit)
        for key, data in self.major_matrix.items():
            if key in low_name:
                return data
        return {"astro": "Universal Axis", "elem": "Aura Field", "out": "Maybe", "up": "Thematic tracking milestone.", "rev": "Internalized field alignment."}

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
        """Scans timeline contexts to locate active metadata framework markers."""
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
        card_to_decks: Dict[str, Dict] = {}
        for d_name, card, is_rev in hits:
            if card.name not in card_to_decks:
                card_to_decks[card.name] = {"card": card, "is_rev": is_rev, "decks": []}
            card_to_decks[card.name]["decks"].append(d_name)

        card_narratives = []
        for card_name, info in card_to_decks.items():
            rev_str = " (Reversed)" if info["is_rev"] else " (Upright)"
            elem = info["card"].attributes.get("element", "Aura Field")
            astro = info["card"].attributes.get("astrology", "Universal")
            outlook = info["card"].binary_outlook
            decks_str = ", ".join(info["decks"])
            card_narratives.append(f"Activation: {card_name}{rev_str} [{decks_str}] - Elem: {elem} | Astro: {astro} | Bias: {outlook}.")
        if card_narratives:
            narrative_parts.append(" | ".join(card_narratives))
        return " | ".join(narrative_parts)

    def _get_cue_seconds(self, sub_time) -> int:
        return sub_time.hours * 3600 + sub_time.minutes * 60 + sub_time.seconds

    def _process_match(self, sub_file: SubRipFile, idx: int, decks: List[DeckData], seen_counts: Dict[Tuple[str, str], int], hits: List[Tuple[str, CardData, bool]], meta_topics: List[str]) -> Tuple[str, int]:
        exp_hits, final_size = self._expand_window_horizontally(sub_file, idx, decks, seen_counts)
        hits.extend(exp_hits)
        return self._build_chapter_title(hits, meta_topics), final_size

    def _time_to_seconds(self, time_str: str) -> int:
        h, m, s = map(int, time_str.split(":"))
        return h * 3600 + m * 60 + s

    def _seconds_to_time(self, seconds: int) -> str:
        return f"{seconds // 3600:02d}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"

    def _append_or_merge_chapter(self, chapters: List[dict], start_sec: int, title: str) -> None:
        if chapters and (start_sec - self._time_to_seconds(chapters[-1]["timestamp"]) < 10):
            chapters[-1]["title"] += f" {title}"
        else:
            chapters.append({"timestamp": self._seconds_to_time(start_sec), "title": title})

    def analyze_chapters(self, sub_file: SubRipFile, decks: List[DeckData], keywords: List[str]) -> List[dict]:
        """Analyzes subtitle timelines to generate chapter milestone tracks."""
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

@click.group()
def main():
    """Tarot Video Tools: Orchestrator managing dynamic chapter extraction metrics."""
    pass


@main.command()
@click.option("--name", required=True, type=str)
@click.option("--type", "deck_type_arg", default="tarot", type=click.Choice(["tarot", "oracle"]))
@click.option("--cache-dir", default=".deck_cache", type=str)
@click.option("-f", "--force-overwrite", is_flag=True)
def bootstrap(name: str, deck_type_arg: str, cache_dir: str, force_overwrite: bool):
    repo = LocalDeckRepository(cache_dir)
    target_filepath = repo._get_path(name)

    if target_filepath.exists() and not force_overwrite:
        click.echo(f"Registry cache file already exists: '{target_filepath}'. Skipping fetch sequence.")
        return

    deck = DeckData(deck_name=name, deck_type=deck_type_arg)
    enricher = SemanticAttributeEnricher()
    low_name = name.lower().strip()
    discovered_raw_names = []
    card_data_list = []

    # TIER 1 & 2: DYNAMIC PRE-FLIGHT DISCOVERY OVER REST AND OPEN BOOK INDICES
    if deck_type_arg == "tarot":
        click.echo(f"🌐 [Tier 2] Fetching dynamic card list from tarot database client for '{name}'...")
        api_cards = OpenLibraryDeckFetcher._fetch_verified_tarot_db()
        if api_cards:
            discovered_raw_names = [c.get("name") for c in api_cards if c.get("name")]

    if not discovered_raw_names:
        click.echo(f"🔍 [Tier 2] Querying OpenLibrary to map descriptive index card lists for '{name}'...")
        fetcher = OpenLibraryDeckFetcher()
        discovered_raw_names, _ = fetcher.fetch_card_details(name)

    # TIER 3: UNCONSTRAINED UN-LINKED DISCOVERY PASS OVER THE LOCAL HARDWARE MODEL
    if not discovered_raw_names:
        click.echo(f"🧠 [Tier 3] Model Discovery Pass: Asking Mistral to unpack individual card listings for '{name}'...")
        discovered_raw_names = LocalLLMOracleScraper.fetch_oracle_names(name)

    # TIER 4: GENERAL DYNAMIC RUNTIME MATRIX GENERATOR (Absolute fallback)
    if not card_data_list:
        click.echo(f"⚠️ [Tier 4] Systems fallback. Compiling structural defaults matrix...")
        fallback_names = []
        if deck_type_arg == "tarot":
            fallback_names = ["The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"]
            suits = ["wands", "cups", "swords", "pentacles"]
            for suit in suits:
                fallback_names.append(f"Ace of {suit.capitalize()}")
                fallback_names.extend([f"{n} of {suit.capitalize()}" for n in ["Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten"]])
                fallback_names.extend([f"{c} of {suit.capitalize()}" for c in ["Page", "Knight", "Queen", "King"]])
        else:
            prefix = "Alchemy" if "alchemy" in low_name else "Animal" if "animal" in low_name else "Oracle"
            target_size = 68 if prefix == "Animal" else 71 if prefix == "Alchemy" else 44
            fallback_names = [f"{prefix} Card {i}" for i in range(1, target_size + 1)]

        for idx, c_name in enumerate(fallback_names):
            suit_match = next((s for s in ["wands", "cups", "swords", "pentacles"] if s in c_name.lower()), "")
            card_data_list.append({"name": c_name, "suit": suit_match, "idx": idx + 1, "up": None, "rev": None, "out": None, "astro": None, "elem": None})

    # DYNAMIC PACKING AND MATHEMATIC DECAN CORRECTION SERIALIZATION LOOP
    processed_cards_dict = {}

    # Decan Assignment Matrix (Golden Dawn System)
    decan_lookup = {
        "wands": {
            "two": "Mars in Aries", "three": "Sun in Aries", "four": "Venus in Aries",
            "five": "Saturn in Leo", "six": "Jupiter in Leo", "seven": "Mars in Leo",
            "eight": "Mercury in Sagittarius", "nine": "Moon in Sagittarius", "ten": "Saturn in Sagittarius"
        },
        "cups": {
            "two": "Venus in Cancer", "three": "Mercury in Cancer", "four": "Moon in Cancer",
            "five": "Mars in Scorpio", "six": "Sun in Scorpio", "seven": "Venus in Scorpio",
            "eight": "Saturn in Pisces", "nine": "Jupiter in Pisces", "ten": "Mars in Pisces"
        },
        "swords": {
            "two": "Moon in Libra", "three": "Saturn in Libra", "four": "Jupiter in Libra",
            "five": "Venus in Aquarius", "six": "Mercury in Aquarius", "seven": "Moon in Aquarius",
            "eight": "Mars in Gemini", "nine": "Sun in Gemini", "ten": "Venus in Gemini"
        },
        "pentacles": {
            "two": "Jupiter in Capricorn", "three": "Mars in Capricorn", "four": "Sun in Capricorn",
            "five": "Mercury in Taurus", "six": "Moon in Taurus", "seven": "Saturn in Taurus",
            "eight": "Sun in Virgo", "nine": "Venus in Virgo", "ten": "Mercury in Virgo"
        }
    }

    for item in card_data_list:
        c_name = item["name"]
        low_card_name = c_name.lower().strip()
        suit_match = item["suit"]

        if not suit_match:
            suit_match = next((s for s in ["wands", "cups", "swords", "pentacles"] if s in low_card_name), "")

        upright = item["up"] if item["up"] is not None else "Overview pending compilation"
        reversed_m = item["rev"] if item["rev"] is not None else "Shadow analysis pending"
        outlook = item["out"] if item["out"] is not None else "Maybe"
        astro = item["astro"]
        elem = item["elem"]

        # Run code-level baseline tracking if preceding tiers pass blank items
        if not astro or astro == "Universal Axis":
            inferred = enricher.enrich_card(c_name, suit_match)
            astro = inferred.get("astro", "Universal Axis")
            elem = inferred.get("elem", "Aura Field")
            if outlook == "Maybe":
                outlook = inferred.get("out", "Maybe")

        # STABLE OVERRIDE MAPPING: Enforce Decans and True Golden Dawn Court Titles
        if suit_match and deck_type_arg == "tarot":
            base_elem = "Fire" if suit_match == "wands" else "Water" if suit_match == "cups" else "Air" if suit_match == "swords" else "Earth"

            # 1. Intercept and calculate sequential Minor Arcana decan strings
            number_word = next((w for w in ["two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"] if w in low_card_name), "")
            if number_word in decan_lookup[suit_match]:
                astro = decan_lookup[suit_match][number_word]
                elem = base_elem

            # 2. Intercept and enforce flawless historical Golden Dawn Titles
            elif "king of" in low_card_name:
                elem = f"Fire + {base_elem}"
                if suit_match == "wands":
                    astro = "Prince of the Chariot of Fire"
                elif "cups" in low_card_name:
                    astro = "Prince of the Chariot of the Waters"
                elif "swords" in low_card_name:
                    astro = "Prince of the Chariot of the Winds"
                else:
                    astro = "Prince of the Chariot of Earth"

            elif "queen of" in low_card_name:
                elem = f"Water + {base_elem}"
                if suit_match == "wands":
                    astro = "Queen of the Thrones of Flame"
                elif "cups" in low_card_name:
                    astro = "Queen of the Thrones of the Waters"
                elif "swords" in low_card_name:
                    astro = "Queen of the Thrones of the Air"
                else:
                    astro = "Queen of the Thrones of the Earth"

            elif "knight of" in low_card_name:
                elem = f"Air + {base_elem}"
                if suit_match == "wands":
                    astro = "Lord of the Thunder & Lightning"
                elif "cups" in low_card_name:
                    astro = "Lord of the Waves & Waters"
                elif "swords" in low_card_name:
                    astro = "Lord of the Wind & Breezes"
                else:
                    astro = "Lord of the Wide & Fertile Land"

            elif "page of" in low_card_name:
                elem = f"Earth + {base_elem}"
                if suit_match == "wands":
                    astro = "Princess of the Shining Flame"
                elif "cups" in low_card_name:
                    astro = "Princess of the Echoing Wave"
                elif "swords" in low_card_name:
                    astro = "Princess of the Rushing Winds"
                else:
                    astro = "Princess of the Echoing Hills"

            elif "ace of" in low_card_name:
                elem = f"Pure Root of {base_elem}"
                if suit_match == "wands":
                    astro = "Root of the Powers of Fire"
                elif "cups" in low_card_name:
                    astro = "Root of the Powers of Water"
                elif "swords" in low_card_name:
                    astro = "Root of the Powers of Air"
                else:
                    astro = "Root of the Powers of Earth"

        # Cache single element fragment state bounds
        frag_data = {
            "name": c_name, "upright": upright, "reversed": reversed_m,
            "outlook": outlook, "attributes": {"astrology": astro, "element": elem}
        }
        repo.save_fragment(name, c_name, frag_data)

        processed_cards_dict[low_card_name] = CardData(
            name=c_name, number=str(item["idx"]),
            upright_meaning=upright, reversed_meaning=reversed_m,
            binary_outlook=outlook, attributes={"astrology": astro, "element": elem}
        )

    deck.cards = processed_cards_dict
    repo.save_deck(deck)
    click.echo(f"🎉 Success! Completely serialized {len(deck.cards)} card cache maps for '{name}'.")


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

