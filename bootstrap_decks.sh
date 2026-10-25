#!/bin/bash

# Exit immediately if any bootstrapping sequence returns errors
set -e

echo "=========================================================================="
echo "📦 Initializing Local Tarot Deck Repositories & Registries"
echo "=========================================================================="

# Create target cache paths cleanly
mkdir -p .deck_cache

echo "Seeding default archetypal card catalogs into local persistent memory matrix..."

# 1. Seed flagship baseline Rider Waite layouts
poetry run tarot-chapters bootstrap --name "Rider Waite Tarot" --type "tarot"

# 2. Seed lowercase alternative string mappings for loose threshold tracking overrides
poetry run tarot-chapters bootstrap --name "rider waite" --type "tarot"

# 3. Seed deep ceremonial layouts
poetry run tarot-chapters bootstrap --name "Hermetic Tarot" --type "tarot"

echo -e "\nVerification: Reviewing active workspace deck caches..."
ls -la .deck_cache/

echo -e "\n=========================================================================="
echo "🎉 Local environment bootstrap operation completed successfully!"
echo "=========================================================================="

