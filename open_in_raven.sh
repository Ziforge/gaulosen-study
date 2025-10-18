#!/bin/bash
#
# Automated Raven Pro Opener
# Opens audio files with their corresponding selection tables in Raven Pro
#

echo "🐦 Opening Gaulossen Analysis in Raven Pro"
echo "=========================================="
echo ""

# Paths
RAVEN_APP="/Applications/Raven Pro 1.6/Raven Pro.app"
AUDIO_DIR="/Users/georgeredpath/Dev/Gaulossen-recordings/audio_files"
RAVEN_TABLES="/Users/georgeredpath/Dev/mcp-pipeline/shared/gaulossen/results/raven_mcp_converted"

# Check if Raven Pro is installed
if [ ! -d "$RAVEN_APP" ]; then
    echo "❌ Error: Raven Pro not found at: $RAVEN_APP"
    exit 1
fi

# Find all Raven selection tables
TABLES=($(ls "$RAVEN_TABLES"/*_raven.txt 2>/dev/null))

if [ ${#TABLES[@]} -eq 0 ]; then
    echo "❌ Error: No Raven selection tables found in $RAVEN_TABLES"
    exit 1
fi

echo "📊 Found ${#TABLES[@]} Raven selection tables"
echo ""
echo "Opening files in Raven Pro:"
echo ""

# Open each selection table
# Raven Pro will prompt to locate the audio file if needed
for table in "${TABLES[@]}"; do
    basename=$(basename "$table")
    echo "   📄 $basename"

    # Open selection table in Raven Pro
    open -a "$RAVEN_APP" "$table"

    # Small delay to prevent overwhelming the app
    sleep 1
done

echo ""
echo "✅ Done! Raven Pro should now be open with your selection tables."
echo ""
echo "📖 Next steps in Raven Pro:"
echo "   1. If prompted, locate the corresponding audio file"
echo "   2. View detections on the spectrogram"
echo "   3. Listen to and verify bird calls"
echo "   4. Edit/annotate as needed"
echo "   5. Export verified selections when done"
echo ""
