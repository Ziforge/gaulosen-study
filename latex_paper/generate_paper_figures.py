#!/usr/bin/env python3
"""
Generate figures for LaTeX paper from Gaulosen study data
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from pathlib import Path

# Set publication-quality style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")

# Paths
RESULTS_DIR = Path('../results')
FIGURES_DIR = Path('figures')

def generate_temporal_distribution():
    """Generate hourly detection pattern figure"""
    hourly_df = pd.read_csv(RESULTS_DIR / 'verified_hourly_activity.csv')

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.bar(hourly_df['hour'], hourly_df['detections'],
           color='steelblue', alpha=0.7, edgecolor='black', linewidth=0.5)

    ax.set_xlabel('Hour of Day', fontsize=11)
    ax.set_ylabel('Number of Detections', fontsize=11)
    ax.set_title('Temporal Distribution of Bird Detections', fontsize=12, fontweight='bold')
    ax.set_xticks(range(0, 24, 2))
    ax.grid(True, alpha=0.3, linestyle='--')

    # Highlight nocturnal period
    ax.axvspan(0, 6, alpha=0.1, color='navy', label='Nocturnal migration period')
    ax.legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'temporal_distribution.png', dpi=300, bbox_inches='tight')
    print("✓ Created temporal_distribution.png")
    plt.close()


def generate_cooccurrence_network():
    """Generate species co-occurrence network figure"""
    cooccur_df = pd.read_csv(RESULTS_DIR / 'verified_co_occurrences.csv')

    # Filter for strongest co-occurrences (top 30 pairs)
    cooccur_df = cooccur_df.nlargest(30, 'co_occurrence_count')

    # Create network graph
    G = nx.Graph()

    for _, row in cooccur_df.iterrows():
        sp1 = row['species_1']
        sp2 = row['species_2']
        weight = row['co_occurrence_count']
        G.add_edge(sp1, sp2, weight=weight)

    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Draw edges with width based on co-occurrence count
    edges = G.edges()
    weights = [G[u][v]['weight'] for u, v in edges]
    max_weight = max(weights)

    nx.draw_networkx_edges(
        G, pos, width=[w/max_weight*3 for w in weights],
        alpha=0.4, edge_color='gray', ax=ax
    )

    # Draw nodes
    node_sizes = [G.degree(node) * 100 for node in G.nodes()]
    nx.draw_networkx_nodes(
        G, pos, node_size=node_sizes,
        node_color='steelblue', alpha=0.7, ax=ax
    )

    # Draw labels with smaller font for readability
    nx.draw_networkx_labels(
        G, pos, font_size=7, font_weight='bold', ax=ax
    )

    ax.set_title('Species Co-occurrence Network\n(Top 30 Associations)',
                 fontsize=12, fontweight='bold', pad=20)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'cooccurrence_network.png', dpi=300, bbox_inches='tight')
    print("✓ Created cooccurrence_network.png")
    plt.close()


def main():
    """Generate all figures for paper"""
    print("Generating figures for LaTeX paper...")
    print(f"Results directory: {RESULTS_DIR.absolute()}")
    print(f"Figures directory: {FIGURES_DIR.absolute()}")

    FIGURES_DIR.mkdir(exist_ok=True)

    try:
        generate_temporal_distribution()
    except Exception as e:
        print(f"✗ Error generating temporal distribution: {e}")

    try:
        generate_cooccurrence_network()
    except Exception as e:
        print(f"✗ Error generating co-occurrence network: {e}")

    print("\nFigure generation complete!")
    print("\nFigures created:")
    for fig in FIGURES_DIR.glob('*.png'):
        size_mb = fig.stat().st_size / 1024 / 1024
        print(f"  - {fig.name} ({size_mb:.2f} MB)")


if __name__ == '__main__':
    main()
