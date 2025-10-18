#!/usr/bin/env python3
"""
Generate interactive review page with pass/fail checkboxes for all detections
"""

import pandas as pd
from pathlib import Path

print("Generating review page...")

# Load review data - use best per species
df = pd.read_csv('results/review_best_per_species.csv')
df = df.sort_values('confidence', ascending=False)

print(f"Loaded {len(df)} detections for review")

# Start HTML
html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gaulossen Detection Review</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }

        .header {
            background: #2c3e50;
            color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }

        .header h1 {
            margin-bottom: 10px;
        }

        .progress {
            background: #34495e;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }

        .progress-bar {
            background: #ecf0f1;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
        }

        .progress-fill {
            background: #27ae60;
            height: 100%;
            transition: width 0.3s;
        }

        .stats {
            display: flex;
            gap: 20px;
            margin-top: 10px;
            flex-wrap: wrap;
        }

        .stat {
            background: #34495e;
            padding: 10px 15px;
            border-radius: 5px;
        }

        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
        }

        .detection-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-left: 5px solid #3498db;
        }

        .detection-card.passed {
            border-left-color: #27ae60;
            background: #f0fff4;
        }

        .detection-card.failed {
            border-left-color: #e74c3c;
            background: #fff5f5;
        }

        .detection-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }

        .species-name {
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
        }

        .confidence {
            font-size: 1.2em;
            font-weight: bold;
            padding: 5px 15px;
            background: #3498db;
            color: white;
            border-radius: 20px;
        }

        .metadata {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            flex-wrap: wrap;
            font-size: 0.9em;
            color: #666;
        }

        .spectrogram {
            max-width: 100%;
            border-radius: 5px;
            margin: 15px 0;
            border: 2px solid #ddd;
        }

        .audio-player {
            margin: 15px 0;
        }

        .audio-player audio {
            width: 100%;
        }

        .review-controls {
            display: flex;
            gap: 15px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 2px solid #eee;
        }

        .review-btn {
            flex: 1;
            padding: 15px;
            font-size: 1.1em;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .pass-btn {
            background: #27ae60;
            color: white;
        }

        .pass-btn:hover {
            background: #229954;
        }

        .fail-btn {
            background: #e74c3c;
            color: white;
        }

        .fail-btn:hover {
            background: #c0392b;
        }

        .skip-btn {
            background: #95a5a6;
            color: white;
        }

        .skip-btn:hover {
            background: #7f8c8d;
        }

        .export-section {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .export-btn {
            background: #3498db;
            color: white;
            padding: 15px 30px;
            font-size: 1.1em;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
        }

        .export-btn:hover {
            background: #2980b9;
        }

        .detection-id {
            font-family: monospace;
            color: #7f8c8d;
            font-size: 0.8em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Detection Review: Gaulossen Nature Reserve</h1>
        <p>Review each detection and mark as PASS (valid bird call) or FAIL (noise/artifact)</p>
        <div class="progress">
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
            </div>
            <div class="stats">
                <div class="stat">
                    <div>Total</div>
                    <div class="stat-value" id="total-count">0</div>
                </div>
                <div class="stat">
                    <div>Reviewed</div>
                    <div class="stat-value" id="reviewed-count">0</div>
                </div>
                <div class="stat" style="background: #27ae60;">
                    <div>Passed</div>
                    <div class="stat-value" id="pass-count">0</div>
                </div>
                <div class="stat" style="background: #e74c3c;">
                    <div>Failed</div>
                    <div class="stat-value" id="fail-count">0</div>
                </div>
            </div>
        </div>
    </div>

    <div id="detections-container">
'''

# Add each detection
for idx, row in df.iterrows():
    detection_id = f"det_{idx}"

    # Check if audio file exists
    audio_path = Path(f"results/audio_clips_enhanced/{row['audio']}")
    audio_exists = audio_path.exists()

    html += f'''
    <div class="detection-card" id="{detection_id}" data-idx="{idx}">
        <div class="detection-header">
            <div class="species-name">{row['species']}</div>
            <div class="confidence">{row['confidence']:.1%}</div>
        </div>
        <div class="metadata">
            <div><strong>Date:</strong> {row['date']}</div>
            <div><strong>Time:</strong> {row['time']}</div>
            <div><strong>Offset:</strong> {row['time_offset']}s</div>
            <div class="detection-id">#{idx + 1} of {len(df)}</div>
        </div>

        <img src="results/spectrograms_best/{row['spectrogram']}"
             alt="{row['species']} spectrogram"
             class="spectrogram">

        <div class="audio-player">
'''

    if audio_exists:
        html += f'''            <audio controls>
                <source src="results/audio_clips_enhanced/{row['audio']}" type="audio/wav">
                Your browser does not support the audio element.
            </audio>
'''
    else:
        html += f'''            <p style="color: #e74c3c;">Audio file not found: {row['audio']}</p>
'''

    html += f'''        </div>

        <div class="review-controls">
            <button class="review-btn pass-btn" onclick="markDetection('{detection_id}', {idx}, 'pass')">
                ✓ PASS - Valid Bird Call
            </button>
            <button class="review-btn fail-btn" onclick="markDetection('{detection_id}', {idx}, 'fail')">
                ✗ FAIL - Noise/Artifact
            </button>
            <button class="review-btn skip-btn" onclick="markDetection('{detection_id}', {idx}, 'skip')">
                ⊘ SKIP - Unsure
            </button>
        </div>
    </div>
'''

# Close HTML and add JavaScript
html += f'''    </div>

    <div class="export-section">
        <h2>Export Results</h2>
        <p>When you're done reviewing, export your results:</p>
        <button class="export-btn" onclick="exportResults()">Download CSV</button>
        <button class="export-btn" onclick="copyResults()">Copy to Clipboard</button>
        <p style="margin-top: 10px; color: #666;">Results are automatically saved to your browser's local storage.</p>
    </div>

    <script>
        const totalDetections = {len(df)};
        const reviews = {{}};

        // Load saved reviews from localStorage
        function loadReviews() {{
            const saved = localStorage.getItem('gaulossen_reviews');
            if (saved) {{
                const savedReviews = JSON.parse(saved);
                Object.assign(reviews, savedReviews);

                // Apply saved states to cards
                for (const [idx, result] of Object.entries(savedReviews)) {{
                    const card = document.getElementById('det_' + idx);
                    if (card) {{
                        card.classList.remove('passed', 'failed');
                        if (result === 'pass') card.classList.add('passed');
                        if (result === 'fail') card.classList.add('failed');
                    }}
                }}
                updateStats();
            }}
        }}

        function markDetection(detectionId, idx, result) {{
            const card = document.getElementById(detectionId);
            card.classList.remove('passed', 'failed');

            if (result === 'pass') {{
                card.classList.add('passed');
                reviews[idx] = 'pass';
            }} else if (result === 'fail') {{
                card.classList.add('failed');
                reviews[idx] = 'fail';
            }} else {{
                delete reviews[idx];
            }}

            // Save to localStorage
            localStorage.setItem('gaulossen_reviews', JSON.stringify(reviews));

            updateStats();

            // Scroll to next unreviewed detection
            scrollToNext(idx);
        }}

        function scrollToNext(currentIdx) {{
            for (let i = currentIdx + 1; i < totalDetections; i++) {{
                if (!reviews.hasOwnProperty(i)) {{
                    const nextCard = document.getElementById('det_' + i);
                    if (nextCard) {{
                        nextCard.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                        return;
                    }}
                }}
            }}
            // If no more unreviewed, scroll to export section
            document.querySelector('.export-section').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}

        function updateStats() {{
            const reviewed = Object.keys(reviews).length;
            const passed = Object.values(reviews).filter(r => r === 'pass').length;
            const failed = Object.values(reviews).filter(r => r === 'fail').length;

            document.getElementById('total-count').textContent = totalDetections;
            document.getElementById('reviewed-count').textContent = reviewed;
            document.getElementById('pass-count').textContent = passed;
            document.getElementById('fail-count').textContent = failed;

            const progress = (reviewed / totalDetections) * 100;
            document.getElementById('progress-fill').style.width = progress + '%';
        }}

        function exportResults() {{
            // Create CSV content
            let csv = 'detection_index,species,confidence,date,time,result\\n';

            const reviewList = [];
            for (let i = 0; i < totalDetections; i++) {{
                const result = reviews[i] || 'unreviewed';
                reviewList.push({{ idx: i, result: result }});
            }}

            // Get detection data from page
            reviewList.forEach(item => {{
                const card = document.getElementById('det_' + item.idx);
                if (card) {{
                    const species = card.querySelector('.species-name').textContent;
                    const confidence = card.querySelector('.confidence').textContent;
                    const date = card.querySelector('.metadata').textContent.match(/Date: ([\\d-]+)/)[1];
                    const time = card.querySelector('.metadata').textContent.match(/Time: ([\\d:]+)/)[1];
                    csv += `${{item.idx}},"${{species}}","${{confidence}}","${{date}}","${{time}}","${{item.result}}"\\n`;
                }}
            }});

            // Download CSV
            const blob = new Blob([csv], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'gaulossen_review_results.csv';
            a.click();
        }}

        function copyResults() {{
            const passed = Object.values(reviews).filter(r => r === 'pass').length;
            const failed = Object.values(reviews).filter(r => r === 'fail').length;
            const total = Object.keys(reviews).length;

            const text = `Gaulossen Detection Review Results:\\n` +
                        `Total reviewed: ${{total}} / ${{totalDetections}}\\n` +
                        `Passed: ${{passed}}\\n` +
                        `Failed: ${{failed}}\\n` +
                        `Pass rate: ${{(passed/total*100).toFixed(1)}}%`;

            navigator.clipboard.writeText(text).then(() => {{
                alert('Results copied to clipboard!');
            }});
        }}

        // Initialize
        document.getElementById('total-count').textContent = totalDetections;
        loadReviews();
    </script>
</body>
</html>
'''

# Write HTML file
output_path = Path('website/review.html')
output_path.write_text(html)

print(f"✅ Review page generated: {output_path}")
print(f"   {len(df)} detections ready for review")
print(f"\nOpen website/review.html in your browser to start reviewing")
