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
---

## 🎙️ Subtitle Extraction (Audio Transcription)

The project includes an advanced audio transcription utility (`extract_subs.py`) that leverages optimized **CTranslate2 Whisper** models to convert spoken video dialogue directly into clean, timestamped SubRip (`.srt`) files.

By default, it uses the highly efficient **`eepdml/faster-whisper-large-v3-turbo-ct2`** model, which offers near-perfect accuracy with blazing-fast transcription speeds.

### 📦 Prerequisites & Installation

Ensure you have initialized your environment with the core audio processing dependencies:

```bash
poetry add faster-whisper
```

*Note: For GPU acceleration on Linux machines, ensure your system has appropriate `cuda` and `cuDNN` libraries installed.*

---

### 🚀 Usage & Examples

The script automatically detects whether to run on CPU or GPU frameworks based on your arguments. By default, it saves the generated `.srt` file **directly alongside the input video file** using the same base name.

#### 1. Optimization for Apple Silicon (M5 Pro / macOS)
Maximize your Mac's efficiency by using high-performance CPU multi-threading combined with `int8` quantization. Adjust threads based on your specific M5 Pro core configuration (e.g., 6–8 threads balances speed and thermal footprint):

```bash
poetry run python src/tarot_vid_tools/extract_subs.py \
  ~/Movies/input_video.mov \
  --device cpu \
  --compute-type int8 \
  --threads 8
```

#### 2. High-Core Count Linux Box (CPU-Only)
Scale processing across deep multi-core server environments by boosting thread workers:

```bash
poetry run python src/tarot_vid_tools/extract_subs.py \
  /path/to/video.mp4 \
  --device cpu \
  --compute-type int8 \
  --threads 16
```

#### 3. NVIDIA CUDA Accelerated Linux Box (GPU)
For machines equipped with modern NVIDIA cards, unlock maximum throughput utilizing native `float16` precision:

```bash
poetry run python src/tarot_vid_tools/extract_subs.py \
  /path/to/video.mp4 \
  --device cuda \
  --compute-type float16
```

---

### ⚙️ Command-Line Arguments Reference

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `video_path` | `str` | *Required* | Path to the target input video file. |
| `-o`, `--output` | `str` | `None` | Custom path to save the `.srt` file. (Defaults next to video file). |
| `-m`, `--model` | `str` | `eepdml/...` | HuggingFace CTranslate2 Whisper model identifier key. |
| `-d`, `--device` | `str` | `cpu` | Computational engine device type. Choices: `cpu`, `cuda`. |
| `-c`, `--compute-type`| `str` | `int8` | Quantization precision framework (`int8`, `float16`, `int8_float16`). |
| `-t`, `--threads` | `int` | `4` | Worker threads assigned to CPU operational matrix blocks. |

To view the complete self-documenting CLI helper directly inside your terminal, execute:
```bash
poetry run python src/tarot_vid_tools/extract_subs.py --help
```

