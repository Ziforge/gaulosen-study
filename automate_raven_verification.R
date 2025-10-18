#!/usr/bin/env Rscript
# Automated Raven Pro Verification using Rraven
# Automates import, measurement, and quality control of bird detections

# Install Rraven if not already installed
if (!requireNamespace("Rraven", quietly = TRUE)) {
  install.packages("Rraven")
}

library(Rraven)

cat("=============================================================================\n")
cat("🔊 AUTOMATED RAVEN PRO VERIFICATION WITH RRAVEN\n")
cat("=============================================================================\n\n")

# Configuration
RAVEN_TABLES_DIR <- "results/verification_reports"
AUDIO_DIR <- "/Users/georgeredpath/Dev/Gaulossen-recordings/audio_files"
OUTPUT_DIR <- "results/rraven_automated"

# Create output directory
dir.create(OUTPUT_DIR, showWarnings = FALSE, recursive = TRUE)

cat("📊 Configuration:\n")
cat(sprintf("   Raven tables: %s\n", RAVEN_TABLES_DIR))
cat(sprintf("   Audio files: %s\n", AUDIO_DIR))
cat(sprintf("   Output: %s\n\n", OUTPUT_DIR))

# ==============================================================================
# STEP 1: Import High Priority Raven Selection Tables
# ==============================================================================

cat("📥 Step 1: Importing high priority Raven selection tables...\n")
cat("-----------------------------------------------------------------------------\n")

high_priority_files <- list.files(
  path = RAVEN_TABLES_DIR,
  pattern = "*_high_priority_raven\\.txt$",
  full.names = TRUE
)

cat(sprintf("   Found %d high priority files\n\n", length(high_priority_files)))

# Import all high priority selections
all_hp_selections <- data.frame()

for (file in high_priority_files) {
  cat(sprintf("   📄 Importing: %s\n", basename(file)))

  selections <- imp_raven(
    path = dirname(file),
    files = basename(file),
    all.data = TRUE,
    freq.cols = TRUE
  )

  if (nrow(selections) > 0) {
    all_hp_selections <- rbind(all_hp_selections, selections)
    cat(sprintf("      ✅ Imported %d selections\n", nrow(selections)))
  }
}

cat(sprintf("\n   Total high priority selections imported: %d\n\n", nrow(all_hp_selections)))

# ==============================================================================
# STEP 2: Quality Metrics Calculation
# ==============================================================================

cat("📊 Step 2: Calculating quality metrics...\n")
cat("-----------------------------------------------------------------------------\n")

if (nrow(all_hp_selections) > 0) {
  # Calculate duration
  all_hp_selections$duration <- all_hp_selections$`End Time (s)` - all_hp_selections$`Begin Time (s)`

  # Calculate bandwidth
  all_hp_selections$bandwidth <- all_hp_selections$`High Freq (Hz)` - all_hp_selections$`Low Freq (Hz)`

  # Quality flags
  all_hp_selections$flag_short_duration <- all_hp_selections$duration < 0.5
  all_hp_selections$flag_wide_bandwidth <- all_hp_selections$bandwidth > 8000
  all_hp_selections$flag_narrow_bandwidth <- all_hp_selections$bandwidth < 500

  cat(sprintf("   Duration range: %.2f - %.2f seconds\n",
              min(all_hp_selections$duration),
              max(all_hp_selections$duration)))
  cat(sprintf("   Bandwidth range: %.0f - %.0f Hz\n",
              min(all_hp_selections$bandwidth),
              max(all_hp_selections$bandwidth)))
  cat(sprintf("   Short duration flags: %d\n", sum(all_hp_selections$flag_short_duration)))
  cat(sprintf("   Wide bandwidth flags: %d\n", sum(all_hp_selections$flag_wide_bandwidth)))
  cat(sprintf("   Narrow bandwidth flags: %d\n\n", sum(all_hp_selections$flag_narrow_bandwidth)))
}

# ==============================================================================
# STEP 3: Export Enhanced Selection Tables
# ==============================================================================

cat("📤 Step 3: Exporting enhanced selection tables...\n")
cat("-----------------------------------------------------------------------------\n")

if (nrow(all_hp_selections) > 0) {
  # Save combined high priority table
  output_file <- file.path(OUTPUT_DIR, "high_priority_enhanced.txt")
  exp_raven(
    X = all_hp_selections,
    file.name = "high_priority_enhanced",
    path = OUTPUT_DIR,
    sound.file.path = AUDIO_DIR
  )
  cat(sprintf("   ✅ Exported: %s\n", basename(output_file)))

  # Save CSV for analysis
  csv_file <- file.path(OUTPUT_DIR, "high_priority_enhanced.csv")
  write.csv(all_hp_selections, csv_file, row.names = FALSE)
  cat(sprintf("   ✅ Exported: %s\n\n", basename(csv_file)))
}

# ==============================================================================
# STEP 4: Species-Level Summary
# ==============================================================================

cat("📊 Step 4: Generating species-level summary...\n")
cat("-----------------------------------------------------------------------------\n")

if (nrow(all_hp_selections) > 0 && "Common Name" %in% colnames(all_hp_selections)) {
  species_summary <- aggregate(
    cbind(duration, bandwidth, Confidence) ~ `Common Name`,
    data = all_hp_selections,
    FUN = function(x) c(count = length(x), mean = mean(x), sd = sd(x))
  )

  cat("\n   Species Summary:\n")
  for (i in 1:nrow(species_summary)) {
    species <- species_summary[i, "Common Name"]
    count <- species_summary[i, "duration"][1]
    mean_conf <- species_summary[i, "Confidence"][2]

    cat(sprintf("   %s: %d detection(s), confidence %.3f\n",
                species, count, mean_conf))
  }

  # Export species summary
  csv_file <- file.path(OUTPUT_DIR, "species_summary_rraven.csv")
  write.csv(species_summary, csv_file, row.names = FALSE)
  cat(sprintf("\n   ✅ Exported: %s\n\n", basename(csv_file)))
}

# ==============================================================================
# STEP 5: Import All Rare Species Tables
# ==============================================================================

cat("📥 Step 5: Importing rare species Raven selection tables...\n")
cat("-----------------------------------------------------------------------------\n")

rare_species_files <- list.files(
  path = RAVEN_TABLES_DIR,
  pattern = "*_rare_species_raven\\.txt$",
  full.names = TRUE
)

cat(sprintf("   Found %d rare species files\n\n", length(rare_species_files)))

all_rare_selections <- data.frame()

for (file in rare_species_files) {
  cat(sprintf("   📄 Importing: %s\n", basename(file)))

  selections <- imp_raven(
    path = dirname(file),
    files = basename(file),
    all.data = TRUE,
    freq.cols = TRUE
  )

  if (nrow(selections) > 0) {
    all_rare_selections <- rbind(all_rare_selections, selections)
    cat(sprintf("      ✅ Imported %d selections\n", nrow(selections)))
  }
}

cat(sprintf("\n   Total rare species selections imported: %d\n\n", nrow(all_rare_selections)))

# Export rare species combined table
if (nrow(all_rare_selections) > 0) {
  output_file <- file.path(OUTPUT_DIR, "rare_species_combined.txt")
  exp_raven(
    X = all_rare_selections,
    file.name = "rare_species_combined",
    path = OUTPUT_DIR,
    sound.file.path = AUDIO_DIR
  )
  cat(sprintf("   ✅ Exported: %s\n\n", basename(output_file)))
}

# ==============================================================================
# SUMMARY
# ==============================================================================

cat("=============================================================================\n")
cat("✅ AUTOMATED RAVEN VERIFICATION COMPLETE\n")
cat("=============================================================================\n\n")

cat("📊 Summary:\n")
cat(sprintf("   High priority selections processed: %d\n", nrow(all_hp_selections)))
cat(sprintf("   Rare species selections processed: %d\n", nrow(all_rare_selections)))
cat(sprintf("   Total selections: %d\n\n", nrow(all_hp_selections) + nrow(all_rare_selections)))

cat("📁 Output files in results/rraven_automated/:\n")
cat("   - high_priority_enhanced.txt (Raven format)\n")
cat("   - high_priority_enhanced.csv (for analysis)\n")
cat("   - rare_species_combined.txt (Raven format)\n")
cat("   - species_summary_rraven.csv (statistics)\n\n")

cat("🔧 Next Steps:\n")
cat("   1. Open enhanced selection tables in Raven Pro\n")
cat("   2. Tables now include quality metrics and flags\n")
cat("   3. Review CSV files for statistical analysis\n")
cat("   4. Use combined tables for batch verification\n\n")

cat("💡 Rraven Capabilities Used:\n")
cat("   ✅ imp_raven() - Import Raven selection tables\n")
cat("   ✅ exp_raven() - Export enhanced tables\n")
cat("   ✅ Automated quality metric calculation\n")
cat("   ✅ Batch processing of multiple files\n\n")

cat("📖 For more automation options, see Rraven documentation:\n")
cat("   - run_raven() to launch Raven from R\n")
cat("   - raven_batch_detec() for batch detection\n")
cat("   - extract_ts() for time series analysis\n\n")
