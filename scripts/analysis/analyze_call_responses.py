#!/usr/bin/env python3
"""
Call Response Network Analysis
Analyzes which species respond to each other's calls
Detects alarm cascades, mobbing coordination, and interspecific communication
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import networkx as nx

print("=" * 80)
print("🔗 CALL RESPONSE NETWORK ANALYSIS")
print("=" * 80)
print()

# Load detections
df = pd.read_csv('results/all_detections_with_weather.csv')
df['datetime'] = pd.to_datetime(df['absolute_timestamp'])
df = df.sort_values(['filename', 'start_s'])

print(f"📊 Analyzing {len(df)} detections for response patterns")
print()

# ============================================================================
# DETECT CALL RESPONSES (Species A calls → Species B responds within 10s)
# ============================================================================

response_threshold = 10  # seconds
response_pairs = defaultdict(int)
response_details = []

for filename in df['filename'].unique():
    file_df = df[df['filename'] == filename].sort_values('start_s')

    for i in range(len(file_df) - 1):
        call_1 = file_df.iloc[i]
        call_2 = file_df.iloc[i + 1]

        time_diff = call_2['start_s'] - call_1['end_s']

        # If different species and call 2 within 10s of call 1
        if (call_1['common_name'] != call_2['common_name'] and
            0 < time_diff < response_threshold):

            species_pair = (call_1['common_name'], call_2['common_name'])
            response_pairs[species_pair] += 1

            response_details.append({
                'initiator': call_1['common_name'],
                'responder': call_2['common_name'],
                'time_lag': time_diff,
                'filename': filename,
                'time': call_1['start_s']
            })

print(f"✅ Detected {len(response_details)} call-response events")
print(f"   Unique species pairs: {len(response_pairs)}")
print()

# ============================================================================
# TOP RESPONSE PATTERNS
# ============================================================================

print("=" * 80)
print("TOP CALL-RESPONSE PATTERNS")
print("=" * 80)
print()

# Sort by frequency
sorted_pairs = sorted(response_pairs.items(), key=lambda x: x[1], reverse=True)

print("Species A calls → Species B responds:")
print("-" * 80)
for (initiator, responder), count in sorted_pairs[:20]:
    # Calculate average response time
    pair_responses = [r for r in response_details
                     if r['initiator'] == initiator and r['responder'] == responder]
    avg_lag = np.mean([r['time_lag'] for r in pair_responses])

    print(f"  {initiator:30s} → {responder:30s} | {count:3d}x | Avg lag: {avg_lag:.2f}s")

print()

# ============================================================================
# ALARM CASCADE DETECTION
# ============================================================================

print("=" * 80)
print("ALARM CASCADE DETECTION")
print("=" * 80)
print()
print("Looking for rapid multi-species response chains (alarm/mobbing behavior)")
print()

cascades = []

for filename in df['filename'].unique():
    file_df = df[df['filename'] == filename].sort_values('start_s')

    # Look for ≥3 different species calling within 20 seconds
    for i in range(len(file_df) - 2):
        window = file_df.iloc[i:i+10]  # Check next 10 calls

        if window.iloc[-1]['start_s'] - window.iloc[0]['start_s'] < 20:
            species_in_window = window['common_name'].unique()

            if len(species_in_window) >= 3:
                # Potential alarm cascade
                cascades.append({
                    'filename': filename,
                    'start_time': window.iloc[0]['start_s'],
                    'num_species': len(species_in_window),
                    'num_calls': len(window),
                    'species_list': list(species_in_window),
                    'duration': window.iloc[-1]['start_s'] - window.iloc[0]['start_s']
                })

# Remove duplicates (overlapping windows)
unique_cascades = []
for cascade in cascades:
    is_duplicate = False
    for existing in unique_cascades:
        if (existing['filename'] == cascade['filename'] and
            abs(existing['start_time'] - cascade['start_time']) < 10):
            is_duplicate = True
            break
    if not is_duplicate:
        unique_cascades.append(cascade)

if unique_cascades:
    print(f"✅ Detected {len(unique_cascades)} alarm cascade events")
    print()
    print("Top 10 Alarm Cascades:")
    print("-" * 80)

    sorted_cascades = sorted(unique_cascades, key=lambda x: x['num_species'], reverse=True)

    for cascade in sorted_cascades[:10]:
        print(f"  File: {cascade['filename']}")
        print(f"  Time: {int(cascade['start_time']//3600):02d}:{int((cascade['start_time']%3600)//60):02d}:{int(cascade['start_time']%60):02d}")
        print(f"  Species involved ({cascade['num_species']}): {', '.join(cascade['species_list'][:5])}")
        print(f"  Calls: {cascade['num_calls']} in {cascade['duration']:.1f}s")
        print()
else:
    print("❌ No clear alarm cascades detected")
    print()

# ============================================================================
# NETWORK GRAPH
# ============================================================================

print("=" * 80)
print("CALL-RESPONSE NETWORK")
print("=" * 80)
print()

# Create directed graph
G = nx.DiGraph()

# Add edges with weights
for (initiator, responder), count in response_pairs.items():
    if count >= 3:  # Only strong connections
        G.add_edge(initiator, responder, weight=count)

print(f"Network nodes (species): {len(G.nodes)}")
print(f"Network edges (responses): {len(G.edges)}")
print()

if len(G.nodes) > 0:
    # Most responsive species (high in-degree)
    in_degrees = dict(G.in_degree(weight='weight'))
    out_degrees = dict(G.out_degree(weight='weight'))

    print("Most Responsive Species (frequently respond to others):")
    print("-" * 80)
    for species, degree in sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {species:40s} | {int(degree)} responses")
    print()

    print("Most Initiating Species (others respond to them):")
    print("-" * 80)
    for species, degree in sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {species:40s} | {int(degree)} triggered responses")
    print()

# ============================================================================
# SAVE RESULTS
# ============================================================================

print("=" * 80)
print("💾 SAVING RESULTS")
print("=" * 80)
print()

# Save response pairs
response_df = pd.DataFrame([
    {
        'initiator': init,
        'responder': resp,
        'count': count
    }
    for (init, resp), count in sorted_pairs
])
response_df.to_csv('results/call_response_pairs.csv', index=False)
print("✅ Saved response pairs: results/call_response_pairs.csv")

# Save alarm cascades
if unique_cascades:
    cascade_df = pd.DataFrame([
        {
            'filename': c['filename'],
            'start_time': c['start_time'],
            'num_species': c['num_species'],
            'num_calls': c['num_calls'],
            'duration': c['duration'],
            'species': ', '.join(c['species_list'])
        }
        for c in sorted_cascades
    ])
    cascade_df.to_csv('results/alarm_cascades.csv', index=False)
    print("✅ Saved alarm cascades: results/alarm_cascades.csv")

# Save network edges
if len(G.edges) > 0:
    edge_df = pd.DataFrame([
        {
            'from': u,
            'to': v,
            'weight': d['weight']
        }
        for u, v, d in G.edges(data=True)
    ])
    edge_df.to_csv('results/response_network_edges.csv', index=False)
    print("✅ Saved network: results/response_network_edges.csv")

print()
print("=" * 80)
print("✅ CALL RESPONSE ANALYSIS COMPLETE")
print("=" * 80)
print()
