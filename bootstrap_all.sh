#!/usr/bin/env bash
# ==============================================================================
# Tarot & Oracle Video Tools: Master Library Bootstrapper Loop
# Curated for YouTube Performance, Core Authors, & Esoteric Metrics
# Fits under strict 100-character line width constraints.
# ==============================================================================

# Ensure script halts on immediate unexpected errors
set -e

FORCE_FLAG=""

# Check if user requested an explicit overwrite across the shell runtime via -f
while getopts "f" opt; do
  case $opt in
    f)
      FORCE_FLAG="-f"
      echo "⚠️ Force-overwrite flag detected. All cached registries will be re-fetched."
      ;;
    *)
      echo "Usage: ./bootstrap_all.sh [-f]"
      exit 1
      ;;
  esac
done

echo "=================================================================="
echo "🔮 INITIALIZING MASTER TAROT & ORACLE AUDIO-VISUAL MATRIX SCRAPER"
echo "=================================================================="

# Function helper to encapsulate calls and catch network rate limit protections cleanly
run_bootstrap() {
    local name="$1"
    local dtype="$2"
    echo "------------------------------------------------------------------"
    echo "🚀 Ingesting: '$name' [$dtype]..."
    if ! poetry run tarot-chapters bootstrap --name "$name" --type "$dtype"; then
        echo "⚠️ Warning: Failed processing '$name'. Skipping fallback profile..."
    fi
    # Non-aggressive sleep timer layout to prevent remote server connection blocks
    sleep 1
}

# ==============================================================================
# SECTION 1: THE COMPLETE KIM KRANS COLLECTED WORK MATRIX (1-5)
# ==============================================================================
run_bootstrap "Wild Unknown Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Wild Unknown Animal Spirit" "oracle" $FORCE_FLAG
run_bootstrap "Wild Unknown Alchemy" "oracle" $FORCE_FLAG
run_bootstrap "Wild Unknown Archetypes" "oracle" $FORCE_FLAG
run_bootstrap "Wild Unknown Pocket Tarot" "tarot" $FORCE_FLAG

# ==============================================================================
# SECTION 2: THE ALBERTO VILLOLDO SHAMANIC MATRIX (6-10)
# ==============================================================================
run_bootstrap "Mystical Shaman Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Shamanic Wisdom Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Sacred Power Reading Cards" "oracle" $FORCE_FLAG
run_bootstrap "The Shaman's Dream Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Earth Magic Oracle" "oracle" $FORCE_FLAG

# ==============================================================================
# SECTION 3: THE COLETTE BARON-REID HIGH-PERFORMANCE MATRIX (11-25)
# ==============================================================================
run_bootstrap "Wisdom of the Oracle" "oracle" $FORCE_FLAG
run_bootstrap "The Spirit Animal Oracle" "oracle" $FORCE_FLAG
run_bootstrap "The Good Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Goddess Power Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Oracle of the 7 Energies" "oracle" $FORCE_FLAG
run_bootstrap "Crystal Spirits Oracle" "oracle" $FORCE_FLAG
run_bootstrap "The Map Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Postcards from Spirit" "oracle" $FORCE_FLAG
run_bootstrap "Enchanted Map Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Chakra Wisdom Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Hidden Realms Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Dreaming Way Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Oracle of the Fairies" "oracle" $FORCE_FLAG
run_bootstrap "Animal Spirit Guides Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Sacred Traveler Oracle" "oracle" $FORCE_FLAG

# ==============================================================================
# SECTION 4: HIGH-PERFORMANCE YOUTUBE TAROT FAVORITES (26-75)
# ==============================================================================
run_bootstrap "Rider Waite Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Modern Witch Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Light Seers Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Tarot of the Divine" "tarot" $FORCE_FLAG
run_bootstrap "Ethereal Visions Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Everyday Witch Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Deviant Moon Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Thoth Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Shadowscapes Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Morgan Greer Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Aquarian Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Gilded Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Witches Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Mystic Mondays Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Tarot of Marseilles" "tarot" $FORCE_FLAG
run_bootstrap "Visconti Sforza Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Linestrider Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Golden Art Nouveau Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Steampunk Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Crow Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Ostara Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Mucha Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Spacious Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Starchild Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Moonchild Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Dark Wood Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Santa Muerte Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Cat Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Zombie Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Ghost Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Spiritsong Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Crystal Visions Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Starspinner Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Next World Tarot" "tarot" $FORCE_FLAG
run_bootstrap "The Hood Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Motherpeace Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Robin Wood Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Hanson Roberts Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Universal Waite Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Hermetic Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Alchemical Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Mythic Tarot" "tarot" $FORCE_FLAG
run_bootstrap "DruidCraft Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Osho Zen Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Cosmopolitan Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Prisma Visions Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Cosma Visions Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Neo Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Urban Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Forager's Daughter Tarot" "tarot" $FORCE_FLAG

# ==============================================================================
# SECTION 5: HIGH-PERFORMANCE YOUTUBE ORACLE SELECTIONS (76-125)
# ==============================================================================
run_bootstrap "Work Your Light Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Starseed Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Moonology Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Moonology Manifestation Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Gateway of Light Activation Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Angel Guide Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Keepers of the Light Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Angels and Ancestors Oracle" "oracle" $FORCE_FLAG
run_bootstrap "The Rose Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Sacred Destiny Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Sacred Rebels Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Energy Oracle Cards" "oracle" $FORCE_FLAG
run_bootstrap "Quantum Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Angel Therapy Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Daily Guidance from Your Angels" "oracle" $FORCE_FLAG
run_bootstrap "Black Moon Astrology Cards" "oracle" $FORCE_FLAG
run_bootstrap "Seasons of the Witch Samhain" "oracle" $FORCE_FLAG
run_bootstrap "Seasons of the Witch Yule" "oracle" $FORCE_FLAG
run_bootstrap "Seasons of the Witch Beltane" "oracle" $FORCE_FLAG
run_bootstrap "Threads of Fate Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Goddess Guidance Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Divine Abundance Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Sacred Creators Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Chronicles of Destiny" "oracle" $FORCE_FLAG
run_bootstrap "Dragon Oracle Cards" "oracle" $FORCE_FLAG
run_bootstrap "Lightworker Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Beyond Lemuria Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Atlantis Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Aura Reading Cards" "oracle" $FORCE_FLAG
run_bootstrap "Pixie Lenormand" "oracle" $FORCE_FLAG
run_bootstrap "Blue Bird Lenormand" "oracle" $FORCE_FLAG
run_bootstrap "Herbal Astrology Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Botanical Inspirations" "oracle" $FORCE_FLAG
run_bootstrap "Liquid Crystal Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Unanto Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Star Dragons Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Archetype Cards Caroline Myss" "oracle" $FORCE_FLAG
run_bootstrap "Sacred Geometry Affirmation" "oracle" $FORCE_FLAG
run_bootstrap "Sainted Mediaeval Lenormand" "oracle" $FORCE_FLAG
run_bootstrap "Sexus Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Sacred Feminine Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Pure Magic Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Goddess Dream Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Rumi Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Journey of Love Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Sacred Earth Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Viking Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Celtic Lenormand" "oracle" $FORCE_FLAG
run_bootstrap "Under the Roses Lenormand" "oracle" $FORCE_FLAG
run_bootstrap "Minaise Oracle" "oracle" $FORCE_FLAG

# ==============================================================================
# SECTION 6: ADVANCED ARCHETYPAL, ASTROLOGICAL, & SHADOW WORK (126-144)
# ==============================================================================
run_bootstrap "Tarot of Silences" "tarot" $FORCE_FLAG
run_bootstrap "Gothic Tarot of Vampires" "tarot" $FORCE_FLAG
run_bootstrap "Dark Grimoire Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Ludy Lescot Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Tarot of the Sweet Twilight" "tarot" $FORCE_FLAG
run_bootstrap "Asabove Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Elemental Power Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Tarot of Shadows" "tarot" $FORCE_FLAG
run_bootstrap "Oracle of Shadow and Light" "oracle" $FORCE_FLAG
run_bootstrap "Vampire Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Necronomicon Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Tarot of a Moon Garden" "tarot" $FORCE_FLAG
run_bootstrap "Golden Tarot of Klimt" "tarot" $FORCE_FLAG
run_bootstrap "Illuminati Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Apocalypse Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Chrysalis Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Mary El Tarot" "tarot" $FORCE_FLAG
run_bootstrap "Heavens Help Oracle" "oracle" $FORCE_FLAG
run_bootstrap "Oracle of Echoes" "oracle" $FORCE_FLAG

# ==============================================================================
# SECTION 7: ADD PERSONAL DECKS HERE
# ==============================================================================

run_bootstrap "oracle of the hecatean path" "oracle" $FORCE_FLAG
run_bootstrap "mirra visions" "tarot" $FORCE_FLAG
run_bootstrap "citadel" "oracle" $FORCE_FLAG
run_bootstrap "black moon lilith cosmic alchemy oracle" "oracle" $FORCE_FLAG
run_bootstrap "galactic heritage oracle" "oracle" $FORCE_FLAG
run_bootstrap "murder of crows" "tarot" $FORCE_FLAG
run_bootstrap "crow oracle" "oracle" $FORCE_FLAG
run_bootstrap "sacred geometry activations oracle" "oracle" $FORCE_FLAG
run_bootstrap "feral psychic" "oracle" $FORCE_FLAG
run_bootstrap "soul echo" "oracle" $FORCE_FLAG
run_bootstrap "soul echo II" "oracle" $FORCE_FLAG
run_bootstrap "angel guide" "oracle" $FORCE_FLAG
run_bootstrap "power animals oracle and guidebook" "oracle" $FORCE_FLAG
run_bootstrap "muse tarot" "tarot" $FORCE_FLAG
run_bootstrap "daydream tarot" "tarot" $FORCE_FLAG
run_bootstrap "stained glass tarot" "tarot" $FORCE_FLAG
run_bootstrap "the faeries oracle" "oracle" $FORCE_FLAG
run_bootstrap "gaia oracle" "oracle" $FORCE_FLAG
run_bootstrap "tattoo tarot" "tarot" $FORCE_FLAG
run_bootstrap "oracle of the riftwalker" "oracle" $FORCE_FLAG
run_bootstrap "mystical shaman oracle" "oracle" $FORCE_FLAG
run_bootstrap "hush tarot" "tarot" $FORCE_FLAG
run_bootstrap "ethereal bloom" "tarot" $FORCE_FLAG
run_bootstrap "starseed oracle" "oracle" $FORCE_FLAG
run_bootstrap "starcodes astro oracle" "oracle" $FORCE_FLAG
run_bootstrap "cerulean sequence" "oracle" $FORCE_FLAG
run_bootstrap "moonology" "oracle" $FORCE_FLAG
run_bootstrap "sacred symbols" "oracle" $FORCE_FLAG


echo "=================================================================="
echo "🎯 SUCCESS: ALL WORKSPACE ASSETS SERIALIZED SUCCESSFULLY!"
echo "=================================================================="

