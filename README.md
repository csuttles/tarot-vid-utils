# tarot-vid-tools

An optimized, context-aware command-line platform built in Python using Object-Oriented
Programming (OOP) to ingest video subtitle files (`.srt`) and auto-compile precise YouTube
milestone description chapters for Tarot and Oracle channels.

The platform leverages an adaptive sliding window text analysis algorithm combined with an
external crawling engine to pull asset tokens on-the-fly and map complex esoteric metadata on
the timeline.

---

## 🏗 System Architecture & FHS Layout

The project follows standard Python packaging conventions adhering to the Filesystem Hierarchy
Standard (FHS):

```bash
~/src/tarot-vid-tools/
├── .deck_cache/              # Serialized JSON deck registries (git-ignored)
├── .flake8                   # Local line-length code enforcement constraints
├── pyproject.toml            # Project metadata, scripts, and library dependencies
├── README.md                 # Technical operational documentation
├── src/
│   └── tarot_vid_tools/
│       ├── init.py       # Package namespace descriptor
│       └── generator.py      # Core data models, crawling engine, and Click CLI endpoints
└── tests/
├── init.py           # Automation testing scope marker
└── test_generator.py     # pytest validation scenarios & sequence simulation tests
|__ bootstrap_all.sh.     # convenience script to bootstrap a local cache of 144 popular decks    
```
---

## 📥 Installation & Environment Setup

This project manages its runtime isolation and dependency matrices natively using **Poetry**.

```bash
# Navigate into your development workspace
cd ~/src/tarot-vid-tools/

# Install the project and all production/development dependencies
poetry install
```

## 🛠 Command-Line Interface (CLI) Specification

If you want to jump right in, the convenience script `bootstrap_all.sh` will fetch 144 popular decks to your local cache:

```
bash -x bootstrap_all.sh
```

The utility provides a unified binary command, `tarot-chapters`, exposed via two subcommands:

### 1. `bootstrap` Subcommand
Dynamically queries open metadata repositories (such as the Open Library framework) to discover card
names on-the-fly, maps multi-attribute taxonomy dimensions, and saves them directly to local cache.

```bash
poetry run tarot-chapters bootstrap --name "<deck_name>" [OPTIONS]
```

#### Flags & Options
*   `--name TEXT`: **Required.** Unique descriptive lookup tag to identify the deck.
*   `--type [tarot│oracle]`: Scaffolding engine parsing model template. *(Default: `tarot`)*
*   `--cache-dir TEXT`: Storage volume directory pathway routing. *(Default: `.deck_cache`)*

---

### 2. `parse` Subcommand
Ingests raw video transcripts, tracks spoken context window blocks, isolates card strings, and
compiles timeline chapter metadata tracks.

```bash
poetry run tarot-chapters parse <srt_file_path> --deck <deck_id> [OPTIONS]
```

#### Arguments & Flags
*   `srt_file`: **Required Argument.** System path guiding the app to your target `.srt` subtitle file.
*   `--deck TEXT`: **Required Option (Multiple allowed).** Target cache registry lookup tracking keys.
*   `--output PATH`: Destination path route for the compiled chapters file. Streams to stdout if blank.

---

## 🔮 Multi-Attribute Esoteric Taxonomy

When a deck is initialized via `bootstrap`, the `SemanticAttributeEnricher` engine inspects the
extracted card name tokens and automatically extrapolates the following taxonomic dimensions:

| Dimension Field Key | Decoupled Mapping Functionality | Supported Input Types |
| :--- | :--- | :--- |
| `astrology` | Tracks cosmic planetary spheres, nodes, and decans. | Planets, Nodes, Decans |
| `binary_yes_no` | Provides immediate binary divination parameters. | Yes, No, Neutral |
| `gender` | Establishes target divine gender alignment fields. | Masculine, Feminine, Androgynous |
| `element` | Computes traditional classical and high etheric elements. | Fire, Water, Air, Earth, Æther |
| `jungian` | Maps standard analytical psychological functions. | Anima, Persona, Shadow, Temenos |
| `archetype` | Tracks universal archetypal patterns and card prototypes. | The Innocent, The Portal, The Sage |
| `cosmic` | Defines deep-space waves and stargate portal points. | Interstellar Waves, Crusts |
| `energy` | Evaluates the bio-electric kinetic vibration footprint. | Pure Potential, High Frequency |
| `polarity` | Measures active, passive, or dual state charge matrices. | Active, Passive, Neutral, Dual |

---

## ⚙ Core Processing Mechanics

*   **Dynamic Debouncing:** Merges consecutive card detections occurring within a 10-second window
    into a single milestone element (joined using a `+` delimiter) to keep description tracks clean.
*   **Reversal Tracking:** Scans text surrounding a card hit for orientation modifiers (*"reversed"*,
    *"flipped"*, *"inverted"*, *"upside down"*). If spotted, it appends an explicit `(Reversed)` flag.

---

## 🚀 Execution Workflows & Examples

### Initialize Kyle Gray's Gateway of Light Activation Oracle
```bash
poetry run tarot-chapters bootstrap --name "gateway of light activation oracle" --type oracle
```

### Compile Subtitle Timeline description text files
```bash
poetry run tarot-chapters parse reading.srt --deck gateway_of_light_activation_oracle --output yt.txt
```

---

## 🧪 Automated Testing & Style Verification

```bash
# Run the automated pytest suite (validates lookahead expansion, caching, and reversals)
poetry run pytest

# Execute style and static code checks
poetry run flake8 src/ tests/
poetry run black --check src/ tests/
poetry run pylint src/ tests/
```

