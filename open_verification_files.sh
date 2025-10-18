#!/bin/bash
#
# Open High Priority Verification Files in Raven Pro
# Opens only the detections that need manual verification
#

echo "🔍 Opening High Priority Verification Files in Raven Pro"
echo "========================================================="
echo ""

# Paths
RAVEN_APP="/Applications/Raven Pro 1.6/Raven Pro.app"
VERIFICATION_DIR="/Users/georgeredpath/Dev/mcp-pipeline/shared/gaulossen/results/verification_reports"

# Check if Raven Pro is installed
if [ ! -d "$RAVEN_APP" ]; then
    echo "❌ Error: Raven Pro not found at: $RAVEN_APP"
    exit 1
fi

echo "📊 Priority Verification Files Available:"
echo ""
echo "   1. High Priority (rare + low confidence) - 21 detections"
echo "   2. All Rare Species (single detections) - 27 detections"
echo "   3. All files (complete dataset) - 6,805 detections"
echo ""
echo "Which files would you like to open?"
echo ""
echo "   [1] High priority only (RECOMMENDED)"
echo "   [2] Rare species only"
echo "   [3] Both high priority + rare species"
echo "   [4] All files (not recommended for verification)"
echo "   [q] Quit"
echo ""

read -p "Select option: " choice

case $choice in
    1)
        echo ""
        echo "📂 Opening high priority files (21 detections)..."
        for file in "$VERIFICATION_DIR"/*_high_priority_raven.txt; do
            basename=$(basename "$file")
            echo "   Opening: $basename"
            open -a "$RAVEN_APP" "$file"
            sleep 1
        done
        echo "✅ High priority files opened!"
        ;;

    2)
        echo ""
        echo "📂 Opening rare species files (27 detections)..."
        for file in "$VERIFICATION_DIR"/*_rare_species_raven.txt; do
            basename=$(basename "$file")
            echo "   Opening: $basename"
            open -a "$RAVEN_APP" "$file"
            sleep 1
        done
        echo "✅ Rare species files opened!"
        ;;

    3)
        echo ""
        echo "📂 Opening high priority + rare species files (48 total detections)..."
        for file in "$VERIFICATION_DIR"/*_high_priority_raven.txt "$VERIFICATION_DIR"/*_rare_species_raven.txt; do
            basename=$(basename "$file")
            echo "   Opening: $basename"
            open -a "$RAVEN_APP" "$file"
            sleep 1
        done
        echo "✅ All verification files opened!"
        ;;

    4)
        echo ""
        echo "📂 Opening ALL files (6,805 detections)..."
        RAVEN_TABLES="/Users/georgeredpath/Dev/mcp-pipeline/shared/gaulossen/results/raven_mcp_converted"
        for file in "$RAVEN_TABLES"/*_raven.txt; do
            basename=$(basename "$file")
            echo "   Opening: $basename"
            open -a "$RAVEN_APP" "$file"
            sleep 1
        done
        echo "✅ All files opened!"
        ;;

    q|Q)
        echo "👋 Exiting..."
        exit 0
        ;;

    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "📖 In Raven Pro:"
echo "   - Detections are pre-filtered to show only items needing verification"
echo "   - Review each detection visually and aurally"
echo "   - Edit/delete false positives"
echo "   - Export verified selections when done"
echo ""
echo "📊 Verification Reports:"
echo "   - master_verification_checklist.csv - Complete flagged detections"
echo "   - high_priority_review.csv - Most important (rare + low confidence)"
echo "   - rare_species_review.csv - All single detections"
echo "   - species_confidence_summary.csv - Per-species statistics"
echo ""
