#!/usr/bin/env python3
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

# Load the woodcock audio file
audio_path = '../results/audio_clips/2025-10-13_11h37m_Eurasian_Woodcock_37332s_conf0857.wav'
y, sr = librosa.load(audio_path, sr=None)

# Create figure
fig, ax = plt.subplots(figsize=(8, 4))

# Generate spectrogram
D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
img = librosa.display.specshow(D, y_axis='linear', x_axis='time', sr=sr, ax=ax, cmap='viridis')

# Formatting
ax.set_title('Eurasian Woodcock (Scolopax rusticola)', fontsize=14, fontweight='bold')
ax.set_xlabel('Time (s)', fontsize=12)
ax.set_ylabel('Frequency (Hz)', fontsize=12)
ax.set_ylim(0, 8000)  # Focus on bird vocalization range

# Add colorbar
fig.colorbar(img, ax=ax, format='%+2.0f dB')

# Save
plt.tight_layout()
plt.savefig('figures/spectrogram_woodcock.png', dpi=300, bbox_inches='tight')
print("Woodcock spectrogram saved to figures/spectrogram_woodcock.png")
