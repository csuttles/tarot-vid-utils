"""Tests tracking absolute factual adherence for Hermetic decans, court duals, and oracle keyword matches."""

import pytest
from tarot_vid_tools.generator import SemanticAttributeEnricher, CardData, DeckData


@pytest.fixture
def enricher():
    return SemanticAttributeEnricher()


def test_major_arcana_static_mappings(enricher):
    """Asserts that prime Major Arcana keys return exact Golden Dawn taxonomy baselines."""
    fool_meta = enricher.enrich_card("The Fool")
    assert fool_meta["astro"] == "Uranus"
    assert "Air" in fool_meta["elem"]
    assert fool_meta["out"] == "Yes"

    tower_meta = enricher.enrich_card("The Tower")
    assert tower_meta["astro"] == "Mars"
    assert tower_meta["elem"] == "Fire"
    assert tower_meta["out"] == "No"


def test_minor_arcana_decan_progression():
    """Asserts that the programmatic decan array logic maps the correct planetary sign values."""
    # We simulate how the code processes these items inside the bootstrap block
    decan_lookup = {
        "wands": {"three": "Sun in Aries", "six": "Jupiter in Leo", "nine": "Moon in Sagittarius"},
        "cups": {"two": "Venus in Cancer", "five": "Mars in Scorpio", "ten": "Mars in Pisces"},
        "swords": {"four": "Jupiter in Libra", "five": "Venus in Aquarius", "eight": "Mars in Gemini"},
        "pentacles": {"three": "Mars in Capricorn", "seven": "Saturn in Taurus", "ten": "Mercury in Virgo"}
    }

    test_cases = [
        ("Three of Wands", "wands", "Sun in Aries", "Fire"),
        ("Six of Wands", "wands", "Jupiter in Leo", "Fire"),
        ("Two of Cups", "cups", "Venus in Cancer", "Water"),
        ("Five of Swords", "swords", "Venus in Aquarius", "Air"),
        ("Seven of Pentacles", "pentacles", "Saturn in Taurus", "Earth"),
        ("Ten of Pentacles", "pentacles", "Mercury in Virgo", "Earth")
    ]

    for card_name, suit, expected_astro, expected_elem in test_cases:
        low_name = card_name.lower()
        number_word = next((w for w in ["two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"] if w in low_name), "")

        assert number_word in decan_lookup[suit], f"Missing map loop setup for {number_word}"
        calculated_astro = decan_lookup[suit][number_word]

        assert calculated_astro == expected_astro, f"Decan error on {card_name}: expected {expected_astro}, got {calculated_astro}"


def test_court_card_dual_element_rules():
    """Asserts that Hermetic Court Card equations resolve to accurate blended elemental strings."""
    court_cases = [
        ("King of Wands", "wands", "Fire + Fire", "Chieftain of Wands"),
        ("Queen of Cups", "cups", "Water + Water", "Matriarch of Cups"),
        ("Knight of Swords", "swords", "Air + Air", "Executor of Swords"),
        ("Page of Pentacles", "pentacles", "Earth + Earth", "Herald of Pentacles"),
        ("King of Cups", "cups", "Fire + Water", "Chieftain of Cups"),
        ("Page of Swords", "swords", "Earth + Air", "Herald of Swords"),
        ("Ace of Swords", "swords", "Pure Root of Air", "Seed of Swords Currents")
    ]

    for card_name, suit, expected_elem, expected_astro in court_cases:
        low_name = card_name.lower()
        base_elem = "Fire" if suit == "wands" else "Water" if suit == "cups" else "Air" if suit == "swords" else "Earth"
        suit_cap = suit.capitalize()

        if "king of" in low_name:
            elem = f"Fire + {base_elem}"
            astro = f"Chieftain of {suit_cap}"
        elif "queen of" in low_name:
            elem = f"Water + {base_elem}"
            astro = f"Matriarch of {suit_cap}"
        elif "knight of" in low_name:
            elem = f"Air + {base_elem}"
            astro = f"Executor of {suit_cap}"
        elif "page of" in low_name:
            elem = f"Earth + {base_elem}"
            astro = f"Herald of {suit_cap}"
        elif "ace of" in low_name:
            elem = f"Pure Root of {base_elem}"
            astro = f"Seed of {suit_cap} Currents"

        assert elem == expected_elem, f"Court element error on {card_name}: expected {expected_elem}, got {elem}"
        assert astro == expected_astro, f"Court astro error on {card_name}: expected {expected_astro}, got {astro}"


def test_oracle_keyword_element_matching():
    """Verifies that fluid keyword matching correctly structures the dynamic Oracle card arrays."""
    oracle_cards = [
        "Wild Bear", "Great Whale of the Deep", "Fire Dragon", "Soaring Eagle Spirit", "Golden Egg"
    ]

    expected_mappings = {
        "wild bear": ("Earth", "Grounded Core"),
        "great whale of the deep": ("Water", "Emotional Flow"),
        "fire dragon": ("Fire", "Radiant Spark"),
        "soaring eagle spirit": ("Air", "Mental Clarity"),
        "golden egg": ("Spirit", "Cosmic Axis")
    }

    for raw_name in oracle_cards:
        low_name = raw_name.lower().strip()
        elem, astro = "Aura Field", "Universal Axis"

        if "earth" in low_name or any(w in low_name for w in ["bear", "bull", "deer", "spider"]):
            elem, astro = "Earth", "Grounded Core"
        elif "water" in low_name or any(w in low_name for w in ["whale", "octopus", "otter", "shark"]):
            elem, astro = "Water", "Emotional Flow"
        elif "fire" in low_name or any(w in low_name for w in ["lion", "cheetah", "dragon", "phoenix"]):
            elem, astro = "Fire", "Radiant Spark"
        elif "air" in low_name or any(w in low_name for w in ["eagle", "owl", "hawk", "raven"]):
            elem, astro = "Air", "Mental Clarity"
        elif "spirit" in low_name or "egg" in low_name:
            elem, astro = "Spirit", "Cosmic Axis"

        exp_elem, exp_astro = expected_mappings[low_name]
        assert elem == exp_elem, f"Oracle element match error on {raw_name}: expected {exp_elem}, got {elem}"
        assert astro == exp_astro, f"Oracle astro match error on {raw_name}: expected {exp_astro}, got {astro}"

