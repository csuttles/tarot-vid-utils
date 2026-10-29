#!/bin/bash

# Exit immediately if any bootstrapping sequence returns errors
set -e

FORCE_FLAG=""

# Check if user requested an explicit overwrite across the shell runtime
while getopts "f" opt; do
  case $opt in
    f) FORCE_FLAG="-f" ;;
    *) echo "Usage: ./bootstrap_decks.sh [-f]" ; exit 1 ;;
  esac
done

echo "=========================================================================="
echo "📦 Initializing Local Tarot Deck Repositories & Registries"
echo "=========================================================================="

mkdir -p .deck_cache

echo "Seeding default archetypal card catalogs into local persistent memory matrix..."

# Seed files cleanly using dynamic local cache evaluations
poetry run tarot-chapters bootstrap --name "Rider Waite Tarot" --type "tarot" $FORCE_FLAG
poetry run tarot-chapters bootstrap --name "rider waite" --type "tarot" $FORCE_FLAG
poetry run tarot-chapters bootstrap --name "Hermetic Tarot" --type "tarot" $FORCE_FLAG

echo -e "\nVerification: Reviewing active workspace deck caches..."
ls -la .deck_cache/

echo "=========================================================================="

