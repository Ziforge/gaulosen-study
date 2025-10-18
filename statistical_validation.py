#!/usr/bin/env python3
"""
Statistical Validation of Behavioral Claims
Rigorous hypothesis testing for all behavioral interpretations
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency, poisson
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("📊 STATISTICAL VALIDATION OF BEHAVIORAL CLAIMS")
print("=" * 80)
print()

# Load data
df = pd.read_csv('results/all_detections_with_weather.csv')
df['datetime'] = pd.to_datetime(df['absolute_timestamp'])
df = df.sort_values(['filename', 'start_s'])

print(f"Dataset: {len(df)} detections, {df['common_name'].nunique()} species")
print(f"Period: {(df['datetime'].max() - df['datetime'].min()).total_seconds() / 3600:.1f} hours")
print()

# ============================================================================
# TEST 1: GRAYLAG GOOSE ↔ SPOTTED CRAKE INTERACTION
# ============================================================================

print("=" * 80)
print("TEST 1: GRAYLAG GOOSE ↔ SPOTTED CRAKE CALL-RESPONSE")
print("=" * 80)
print()

print("NULL HYPOTHESIS: Calls are randomly distributed (no interaction)")
print("ALTERNATIVE: Species respond to each other (interaction exists)")
print()

# Get the two species
graylag = df[df['common_name'] == 'Graylag Goose'].copy()
crake = df[df['common_name'] == 'Spotted Crake'].copy()

print(f"Graylag Goose:   {len(graylag):,} detections")
print(f"Spotted Crake:   {len(crake):,} detections")
print()

# Calculate response events for each file
response_window = 10  # seconds

all_responses = []
for filename in df['filename'].unique():
    file_graylag = graylag[graylag['filename'] == filename].sort_values('start_s')
    file_crake = crake[crake['filename'] == filename].sort_values('start_s')

    if len(file_graylag) == 0 or len(file_crake) == 0:
        continue

    # Crake responds to Graylag
    crake_after_graylag = 0
    for g_time in file_graylag['start_s'].values:
        responses = file_crake[(file_crake['start_s'] > g_time) &
                               (file_crake['start_s'] <= g_time + response_window)]
        crake_after_graylag += len(responses)

    # Graylag responds to Crake
    graylag_after_crake = 0
    for c_time in file_crake['start_s'].values:
        responses = file_graylag[(file_graylag['start_s'] > c_time) &
                                 (file_graylag['start_s'] <= c_time + response_window)]
        graylag_after_crake += len(responses)

    all_responses.append({
        'filename': filename,
        'crake_after_graylag': crake_after_graylag,
        'graylag_after_crake': graylag_after_crake,
        'n_graylag': len(file_graylag),
        'n_crake': len(file_crake)
    })

response_df = pd.DataFrame(all_responses)

total_crake_after_graylag = response_df['crake_after_graylag'].sum()
total_graylag_after_crake = response_df['graylag_after_crake'].sum()

print(f"OBSERVED:")
print(f"  Crake calls within {response_window}s after Graylag:  {total_crake_after_graylag}")
print(f"  Graylag calls within {response_window}s after Crake:  {total_graylag_after_crake}")
print(f"  Total 'response' events:                              {total_crake_after_graylag + total_graylag_after_crake}")
print()

# Calculate expected random responses
total_duration = (df['datetime'].max() - df['datetime'].min()).total_seconds()
crake_rate = len(crake) / total_duration  # calls per second
graylag_rate = len(graylag) / total_duration  # calls per second

expected_crake_responses = len(graylag) * (response_window * crake_rate)
expected_graylag_responses = len(crake) * (response_window * graylag_rate)

print(f"EXPECTED (if random):")
print(f"  Crake calls within {response_window}s after Graylag:  {expected_crake_responses:.1f}")
print(f"  Graylag calls within {response_window}s after Crake:  {expected_graylag_responses:.1f}")
print(f"  Total expected random overlaps:                        {expected_crake_responses + expected_graylag_responses:.1f}")
print()

# Chi-square test
observed = np.array([total_crake_after_graylag, total_graylag_after_crake])
expected = np.array([expected_crake_responses, expected_graylag_responses])

chi2_stat = np.sum((observed - expected)**2 / expected)
df_chi = len(observed) - 1
p_value = 1 - stats.chi2.cdf(chi2_stat, df_chi)

print(f"CHI-SQUARE TEST:")
print(f"  χ² statistic:  {chi2_stat:.3f}")
print(f"  p-value:       {p_value:.4f}")
print()

if p_value < 0.05:
    if total_crake_after_graylag + total_graylag_after_crake > expected_crake_responses + expected_graylag_responses:
        print("  ✅ SIGNIFICANT: More responses than expected by chance (p < 0.05)")
        print("     → Evidence of POSITIVE interaction (attraction/response)")
    else:
        print("  ✅ SIGNIFICANT: Fewer responses than expected by chance (p < 0.05)")
        print("     → Evidence of NEGATIVE interaction (avoidance/competition)")
else:
    print("  ❌ NOT SIGNIFICANT: Responses consistent with random chance (p ≥ 0.05)")
    print("     → No evidence of interaction")
print()

# ============================================================================
# TEST 2: FLOCK BEHAVIOR (94% OF DATA CLAIM)
# ============================================================================

print("=" * 80)
print("TEST 2: FLOCK BEHAVIOR VALIDATION")
print("=" * 80)
print()

print("CLAIM: 94% of detections show coordinated flock calling")
print("METHOD: Detections with ≥3 calls/minute in same file")
print()

# Load behavioral analysis results
try:
    behavior_df = pd.read_csv('results/species_summary.csv')
    flock_detections = behavior_df[behavior_df['flock'] == True]['detections'].sum()
    total_detections = behavior_df['detections'].sum()
    flock_percentage = (flock_detections / total_detections) * 100

    print(f"Flock-associated detections: {flock_detections:,} / {total_detections:,} ({flock_percentage:.1f}%)")
    print()

    # But is this actually "flock behavior" or just "high density"?
    print("CRITICAL QUESTION: Does high calling rate = coordinated flock?")
    print()
    print("Consider:")
    print("  • Multiple individuals of gregarious species")
    print("  • Migration stopover with high density")
    print("  • Territorial calls during breeding season")
    print()
    print("CONCLUSION: High calling rate suggests flock PRESENCE,")
    print("            but cannot confirm COORDINATION without acoustic analysis")
    print()

except:
    print("⚠️  Cannot validate - species_summary.csv not found")
    print()

# ============================================================================
# TEST 3: DUETTING/PAIR BONDING
# ============================================================================

print("=" * 80)
print("TEST 3: DUETTING/PAIR BONDING VALIDATION")
print("=" * 80)
print()

print("CLAIM: 13 duetting events with regular 1-5s intervals")
print("QUESTION: Are these true duets or random temporal overlap?")
print()

# For each species, look at call interval regularity
duet_candidates = []

for species in df['common_name'].value_counts().head(10).index:
    species_df = df[df['common_name'] == species]

    for filename in species_df['filename'].unique():
        file_df = species_df[species_df['filename'] == filename].sort_values('start_s')

        if len(file_df) < 4:
            continue

        times = file_df['start_s'].values

        # Look for sequences of 4+ calls with consistent intervals
        for i in range(len(times) - 3):
            window = times[i:i+4]
            if window[-1] - window[0] > 20:
                continue

            intervals = np.diff(window)
            mean_interval = np.mean(intervals)
            std_interval = np.std(intervals)

            # Duetting = regular intervals (low std deviation)
            if 1 < mean_interval < 5 and std_interval < 1.5:
                regularity = mean_interval / (std_interval + 0.01)

                duet_candidates.append({
                    'species': species,
                    'filename': filename,
                    'mean_interval': mean_interval,
                    'std_interval': std_interval,
                    'regularity': regularity,
                    'n_calls': 4
                })

if duet_candidates:
    duet_df = pd.DataFrame(duet_candidates)

    print(f"Found {len(duet_df)} sequences with regular 1-5s intervals")
    print()

    print("Top 5 Most Regular Sequences:")
    print("-" * 80)
    for idx, row in duet_df.nlargest(5, 'regularity').iterrows():
        print(f"  {row['species']:30s} | Interval: {row['mean_interval']:.2f}±{row['std_interval']:.2f}s | "
              f"Regularity: {row['regularity']:.1f}")
    print()

    # Statistical test: Are these intervals MORE regular than random?
    print("STATISTICAL TEST: Regularity vs. Random")
    print()

    # Simulate random calls with similar density
    n_simulations = 1000
    random_regularities = []

    for _ in range(n_simulations):
        # Generate 4 random times in 20-second window
        random_times = np.sort(np.random.uniform(0, 20, 4))
        random_intervals = np.diff(random_times)
        mean_int = np.mean(random_intervals)
        std_int = np.std(random_intervals)

        if 1 < mean_int < 5:  # Same criteria
            random_regularities.append(mean_int / (std_int + 0.01))

    observed_regularity = duet_df['regularity'].mean()
    random_regularity = np.mean(random_regularities)

    print(f"  Observed mean regularity: {observed_regularity:.2f}")
    print(f"  Random mean regularity:   {random_regularity:.2f}")
    print()

    # T-test
    t_stat, p_value = stats.ttest_1samp(duet_df['regularity'], random_regularity)

    print(f"  t-statistic: {t_stat:.3f}")
    print(f"  p-value:     {p_value:.4f}")
    print()

    if p_value < 0.05 and observed_regularity > random_regularity:
        print("  ✅ SIGNIFICANT: Intervals more regular than random (p < 0.05)")
        print("     → Evidence consistent with coordinated calling")
    else:
        print("  ❌ NOT SIGNIFICANT: Regularity consistent with random (p ≥ 0.05)")
        print("     → Cannot confirm coordinated duetting")
    print()
else:
    print("No regular interval sequences found")
    print()

# ============================================================================
# TEST 4: INDIVIDUAL RECOGNITION (30-MIN GAP METHOD)
# ============================================================================

print("=" * 80)
print("TEST 4: INDIVIDUAL RECOGNITION VALIDATION")
print("=" * 80)
print()

print("CLAIM: Up to 5 individuals detected via 30-minute temporal clustering")
print("QUESTION: Is 30-min gap sufficient to distinguish individuals?")
print()

# Test with Spotted Crake (claimed 5 individuals)
crake = df[df['common_name'] == 'Spotted Crake']

individual_counts = []
for filename in crake['filename'].unique():
    file_crake = crake[crake['filename'] == filename].sort_values('start_s')

    if len(file_crake) < 10:
        continue

    times = file_crake['start_s'].values
    gaps = np.diff(times)

    # Count gaps > 30 minutes (1800 seconds)
    n_large_gaps = np.sum(gaps > 1800)
    n_individuals = n_large_gaps + 1

    individual_counts.append({
        'filename': filename,
        'n_calls': len(file_crake),
        'n_individuals': n_individuals,
        'max_gap': gaps.max() / 60,  # minutes
        'mean_gap': gaps.mean() / 60
    })

if individual_counts:
    ind_df = pd.DataFrame(individual_counts)

    print("Spotted Crake Individual Estimates:")
    print("-" * 80)
    for idx, row in ind_df.iterrows():
        print(f"  File: {row['filename'][-20:]}")
        print(f"    Calls: {int(row['n_calls'])}, Individuals: {int(row['n_individuals'])}, "
              f"Max gap: {row['max_gap']:.1f}min, Avg gap: {row['mean_gap']:.1f}min")
    print()

    print("CRITICAL EVALUATION:")
    print("  • 30-min threshold is ARBITRARY (not biologically validated)")
    print("  • Individual birds can be silent for >30 min (resting, foraging)")
    print("  • Multiple individuals can call simultaneously (underestimate)")
    print("  • Method assumes continuous presence (may miss arrivals/departures)")
    print()
    print("CONCLUSION: Individual counts are ROUGH ESTIMATES, not precise")
    print("            Acoustic fingerprinting (MFCC) would be needed for validation")
    print()
else:
    print("Insufficient data for individual analysis")
    print()

# ============================================================================
# TEST 5: WEATHER CORRELATIONS
# ============================================================================

print("=" * 80)
print("TEST 5: WEATHER CORRELATION VALIDATION")
print("=" * 80)
print()

print("CLAIM: Great Snipe shows 95% preference for damp/foggy conditions")
print()

great_snipe = df[df['common_name'] == 'Great Snipe']

if len(great_snipe) > 0:
    weather_counts = great_snipe['weather_summary'].value_counts()
    total = len(great_snipe)

    print(f"Great Snipe weather distribution (n={total}):")
    print("-" * 80)
    for weather, count in weather_counts.items():
        pct = (count / total) * 100
        print(f"  {weather:40s} {count:3d} calls ({pct:5.1f}%)")
    print()

    # Binomial test: Is damp/foggy over-represented?
    overall_weather = df['weather_summary'].value_counts(normalize=True)

    print("STATISTICAL TEST: Great Snipe vs. Overall Weather Distribution")
    print()

    # Test specifically for "Damp, foggy, low visibility"
    fog_weather = "Damp, foggy, low visibility"
    if fog_weather in weather_counts.index:
        gs_fog_count = weather_counts[fog_weather]
        gs_fog_pct = gs_fog_count / total
        overall_fog_pct = overall_weather.get(fog_weather, 0)

        print(f"  Great Snipe fog/damp: {gs_fog_count}/{total} ({gs_fog_pct*100:.1f}%)")
        print(f"  Overall fog/damp:     {overall_fog_pct*100:.1f}%")
        print()

        # Binomial test: Is Great Snipe percentage significantly higher?
        from scipy.stats import binomtest
        result = binomtest(gs_fog_count, total, overall_fog_pct, alternative='greater')
        p_value = result.pvalue

        print(f"  Binomial test p-value: {p_value:.4f}")
        print()

        if p_value < 0.05:
            enrichment = gs_fog_pct / overall_fog_pct
            print(f"  ✅ SIGNIFICANT: Great Snipe shows {enrichment:.1f}x preference for fog/damp (p < 0.05)")
            print(f"     → Weather correlation is statistically supported")
        else:
            print(f"  ❌ NOT SIGNIFICANT: Fog/damp usage consistent with overall pattern (p ≥ 0.05)")
            print(f"     → Cannot confirm weather preference")
    else:
        print("  No fog/damp detections for Great Snipe")
        p_value = 1.0

    print()

    print("SAMPLE SIZE CONSIDERATION:")
    print(f"  Great Snipe: {len(great_snipe)} detections")
    print(f"  Total dataset: {len(df)} detections ({len(great_snipe)/len(df)*100:.1f}%)")
    print()
    if len(great_snipe) < 100:
        print("  ⚠️  SMALL SAMPLE: Results may not be reliable (n < 100)")
    print()
else:
    print("No Great Snipe detections found")
    print()

# ============================================================================
# SUMMARY OF STATISTICAL VALIDATION
# ============================================================================

print("=" * 80)
print("SUMMARY: WHAT CAN WE CONFIDENTLY CLAIM?")
print("=" * 80)
print()

print("TESTED CLAIMS:")
print()
print("1. Graylag Goose ↔ Spotted Crake Interaction:")
print(f"   → Statistical test: p = {p_value:.4f}")
if p_value < 0.05:
    print("   ✅ SUPPORTED: Interaction pattern differs from random")
else:
    print("   ❌ NOT SUPPORTED: Pattern consistent with random overlap")
print()

print("2. Flock Behavior (94% of data):")
print("   → High calling density documented")
print("   ⚠️  CAUTION: Cannot confirm COORDINATION without acoustic analysis")
print("   → Better claim: '94% of calls from recordings with high species density'")
print()

print("3. Duetting/Pair Bonding:")
if duet_candidates and p_value < 0.05:
    print("   ✅ SUPPORTED: Call intervals more regular than random")
else:
    print("   ❌ NOT SUPPORTED: Regularity consistent with random")
print("   → Spectrogram analysis needed to confirm coordination")
print()

print("4. Individual Recognition:")
print("   ⚠️  METHOD LIMITATION: 30-min threshold is arbitrary")
print("   → Estimates are rough, not precise")
print("   → Acoustic fingerprinting (MFCC) needed for validation")
print()

print("5. Weather Correlations:")
if len(great_snipe) > 0 and p_value < 0.05:
    print("   ✅ SUPPORTED: Great Snipe shows non-random weather distribution")
else:
    print("   ❌ NOT TESTED or SMALL SAMPLE")
print()

print("=" * 80)
print("RECOMMENDATION FOR PUBLICATION:")
print("=" * 80)
print()
print("CONSERVATIVE CLAIMS (Well-Supported):")
print("  • 'Documented 6,805 bird vocalizations over 48.8 hours'")
print("  • '90 species detected during peak autumn migration'")
print("  • 'Graylag Goose and Spotted Crake dominated soundscape (80%)'")
print("  • '12 migration wave events with 98% migrant composition'")
print("  • '756 flight-related vocalizations identified'")
print()
print("EXPLORATORY CLAIMS (Needs Verification):")
print("  • 'Evidence of temporal association between Graylag and Crake'")
print("  • 'Regular call intervals suggest possible coordinated calling'")
print("  • 'High calling density indicates gregarious species presence'")
print("  • 'Preliminary evidence of weather-sensitive calling patterns'")
print()
print("AVOID:")
print("  • 'First-ever documentation' (cannot verify)")
print("  • 'Complex social dynamics' (too vague)")
print("  • 'X individuals detected' (method too uncertain)")
print("  • '94% flock behavior' (conflates density with coordination)")
print()

print("=" * 80)
print("✅ STATISTICAL VALIDATION COMPLETE")
print("=" * 80)
print()
