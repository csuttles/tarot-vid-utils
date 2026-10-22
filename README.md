
tarot-vid-tools

An optimized, context-aware command-line utility built in Python using Object-Oriented Programming (OOP) to ingest video subtitle files (.srt) and auto-compile precise YouTube/Vimeo timeline chapter markers for Tarot and Oracle readings.
The system leverages a dynamic sliding window text analysis algorithm cross-referenced against locally cached deck asset dictionaries to identify card names only when spoken within active context windows.

🏗 System Architecture & FHS Layout

The project follows standard Python packaging conventions adhering to the Filesystem Hierarchy Standard (FHS):
~/src/tarot-vid-tools/
├── .deck_cache/              # Hidden directory containing serialized JSON deck registries (git-ignored)
├── .flake8                   # Local line-length code enforcement constraints
├── pyproject.toml            # Project metadata, build configurations, and library dependencies
├── README.md                 # Technical operational documentation
├── src/
│   └── tarot_vid_tools/
│       ├── __init__.py       # Package namespace descriptor
│       └── generator.py      # Core orchestration platform, processing engines, and Click CLI entrypoint
└── tests/
    ├── __init__.py           # Automation testing scope marker
    └── test_generator.py     # Isolated pytest validation scenarios & dynamic sequence evaluation models

📥 Installation & Environment Setup

This project manages its runtime environments and dependencies natively using Poetry.

```bash
# Clone and navigate into your development workspace
cd ~/src/tarot-vid-tools/

# Install the project and all production/development dependencies
poetry install
```


🛠 Command-Line Interface (CLI) Specification

The utility provides a unified binary command, tarot-chapters, exposed via two distinct operational subcommands: bootstrap and parse.

Global Flags

• --cache-dir <path>: Direct path to storage volume housing deck cache assets. (Default: .deck_cache)

1. bootstrap Subcommand

Automates the structural construction of baseline reference master maps so you don't have to populate files manually.

```bash
poetry run tarot-chapters bootstrap --name <deck_id> [OPTIONS]
```


Flags & Options


Flag    Short   Typing  Functional Description  Default
--name  None    STRING  Required. Unique lookup catalog token name for saving the target layout model.  N/A
--type  None    CHOICE  Restricts data scaffolding arrays to validated models (tarot or oracle).    tarot


Operational Behavior

• Tarot Mode: Scaffolds the complete 78-card structure of standard traditional decks (22 Major Arcana + 56 Minor Arcana distributed across Wands, Cups, Swords, and Pentacles).
• Oracle Mode: Generates a minimal generic key structure template equipped with extended metadata dictionaries (attributes), allowing manual tailoring to accommodate highly variable multi-deck layouts.

2. parse Subcommand

Ingests raw video subtitle transcripts, tracks token indices, and compiles properly formatted timeline metadata files.

```bash
```


Arguments & Flags


Parameter   Type    Mode    Description
srt_file    PATH    Positional  Required. Targeted pathing route guiding the system to your input .srt file.
--decks STR LIST    Multi-Flag  Required. Space-separated list of deck cache IDs to cross-reference concurrently during analysis.
--output    PATH    Option  Optional destination route file path. If omitted, streams text directly to stdout.


⚙ Pipeline Component Reference


Data Structure Classes


CardData

• Purpose: Simple encapsulated data carrier defining specific card profiles.
• Attributes: name (Str), number (Optional Str), attributes (Dict mapping custom custom metadata properties).

DeckData

• Purpose: Collection model containing aggregated structures for an entire card deck catalog.
• Methods: to_dict() and from_dict() handle native Python primitives conversions to enable fast serialization.
• Optimization: Converts all target tracking arrays into a lowercased, indexable internal lookup hash table (_normalized_keys) at compilation phase to enforce fast O(1) verification constraints.

Functional Management Utilities


LocalDeckRepository

• Purpose: System persistence layer managing isolated file input/output transactions.
• Optimization (@lru_cache): Core memory pathways optimize file system calls. Path transformations are locked to 32 entries; active JSON file read operations are held via a 16-slot caching buffer to prevent thrashing storage disks when iterating over heavy loops.

OptimizedSlidingWindowAnalyzer

• Purpose: Core contextual heuristic processor.
• Mechanics: Analyzes raw subtitle timelines using a dynamic tracking structure layout:
    1. Advances linearly across lines tracking text blocks via a core interval parameter (base_window_size=4).
    2. Verifies the block text includes the lowercased card registry token and a relevant action verb (e.g., "pull", "drawn", "reveal", "clarify"). This filter eliminates false positives from casual conversational text repeating card terms.
    3. Dynamic Expansion: When a valid combination hits, it balloons the horizon boundary limit up to a max constraint threshold (max_expanded_size=12) to verify if neighboring subtitle lines contain rapid multi-card clusters (e.g., three-card spreads).
    4. Debouncing Protection: Suppresses rapid successive timestamp events firing under a 10-second difference, cleanly blending overlapping hits together with a structural joining delimiter (+).

🚀 Usage Workflows & Examples


1. Scaffolding a Traditional Tarot Deck Template
```bash
poetry run tarot-chapters bootstrap --name rider_waite --type tarot
```

Creates a file named .deck_cache/rider_waite.json filled with the baseline 78-card template maps.

2. Compiling YouTube Chapters from an SRT Track
```bash
poetry run tarot-chapters parse current_reading.srt --decks rider_waite --output youtube_description.txt
```
Processes the transcript file, evaluates text against your rider_waite cache index, and exports production milestones straight to youtube_description.txt.

3. Simultaneous Multi-Deck Ingestion Tracker
```bash
poetry run tarot-chapters parse shadow_work_video.srt --decks rider_waite archetype_oracle
```

Scans both decks at once. If cards from different decks are pulled within the same speech window frame, the analyzer combines them seamlessly:
00:14:32 [rider_waite] The Tower + [archetype_oracle] The Saboteur

🧪 Automated Testing & Style Quality Verification

The project includes a robust automated testing and style verification suite to guarantee codebase reliability:
```bash
# Run the automated pytest suite (validates lookahead expansion, caching, and token normalization)
poetry run pytest

# Execute style enforcement check (ensures clean lines under the 120 character constraint limit)
poetry run flake8 src/ tests/
poetry run black --check src/ tests/

# Execute static code analysis
poetry run pylint src/tarot_vid_tools/
```


