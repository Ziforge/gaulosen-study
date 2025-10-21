#!/usr/bin/env python3
"""
Use a better ML model to verify bird photos.
Using prithivMLmods/Bird-Species-Classifier-526 (89.92% accuracy, 526 species)
"""

import requests
import json
import time
from PIL import Image
from io import BytesIO
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

print("="*80)
print("ML-BASED BIRD PHOTO VERIFICATION - IMPROVED MODEL")
print("Using prithivMLmods/Bird-Species-Classifier-526 (89.92% accuracy)")
print("="*80)
print()

# Load the better bird classification model
print("Loading improved ML model (this may take a minute)...")
try:
    model_name = "prithivMLmods/Bird-Species-Classifier-526"
    processor = AutoImageProcessor.from_pretrained(model_name)
    model = AutoModelForImageClassification.from_pretrained(model_name)
    print(f"✓ Loaded model: {model_name}")
    print(f"  Model supports 526 bird species")
except Exception as e:
    print(f"❌ Could not load model: {e}")
    print("\nTrying alternative model...")
    try:
        model_name = "dennisjooo/Birds-Classifier-EfficientNetB2"
        processor = AutoImageProcessor.from_pretrained(model_name)
        model = AutoModelForImageClassification.from_pretrained(model_name)
        print(f"✓ Loaded model: {model_name}")
    except Exception as e2:
        print(f"❌ Could not load any model: {e2}")
        print("\nPlease install required packages:")
        print("pip install torch transformers pillow")
        exit(1)

print()

# Load existing data
with open('website/species_data.json', 'r', encoding='utf-8') as f:
    species_data = json.load(f)

with open('website/bird_photos.json', 'r', encoding='utf-8') as f:
    photo_data = json.load(f)

def download_image(url):
    """Download image from URL"""
    try:
        response = requests.get(url, timeout=10)
        image = Image.open(BytesIO(response.content))
        return image
    except Exception as e:
        print(f"  ❌ Error downloading image: {e}")
        return None

def classify_bird(image, top_k=5):
    """Classify bird species in image"""
    try:
        # Preprocess image
        inputs = processor(images=image, return_tensors="pt")

        # Run inference
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits

        # Get top predictions
        probs = torch.nn.functional.softmax(logits, dim=-1)
        top_probs, top_indices = torch.topk(probs, top_k)

        predictions = []
        for prob, idx in zip(top_probs[0], top_indices[0]):
            label = model.config.id2label[idx.item()]
            predictions.append({
                'label': label,
                'confidence': prob.item()
            })

        return predictions
    except Exception as e:
        print(f"  ❌ Error classifying: {e}")
        return []

def fuzzy_match(predicted_label, expected_name, expected_scientific):
    """Check if predicted label matches expected species"""
    predicted_lower = predicted_label.lower()

    # Clean up predicted label (remove underscores, numbers, etc.)
    predicted_clean = predicted_lower.replace('_', ' ').replace('-', ' ')

    # Check for exact matches
    if expected_name.lower() in predicted_clean:
        return True
    if expected_scientific.lower() in predicted_clean:
        return True

    # Check for partial matches (genus, common words)
    expected_words = set(expected_name.lower().split())
    predicted_words = set(predicted_clean.split())

    # At least 2 words match or scientific name genus matches
    if len(expected_words & predicted_words) >= 2:
        return True

    # Check scientific name genus
    genus = expected_scientific.split()[0].lower()
    if genus in predicted_clean:
        return True

    # Check if any part of scientific name is in prediction
    scientific_words = set(expected_scientific.lower().split())
    if len(scientific_words & predicted_words) >= 1:
        return True

    return False

# Verify each species
print("Verifying photos...")
print()

verified_correct = []
verified_wrong = []
could_not_verify = []

for idx, sp in enumerate(species_data, 1):
    common_name = sp['common_name']
    scientific_name = sp['scientific_name']

    if common_name not in photo_data:
        continue

    photo = photo_data[common_name]
    image_url = photo.get('image_url', '')

    print(f"[{idx}/{len(species_data)}] {common_name} ({scientific_name})")

    # Download image
    image = download_image(image_url)
    if image is None:
        could_not_verify.append(common_name)
        print("  ⚠️  Could not download image")
        print()
        continue

    # Classify bird
    predictions = classify_bird(image, top_k=10)  # Check top 10
    if not predictions:
        could_not_verify.append(common_name)
        print("  ⚠️  Could not classify image")
        print()
        continue

    # Check if any prediction matches
    match_found = False
    for i, pred in enumerate(predictions):
        if fuzzy_match(pred['label'], common_name, scientific_name):
            verified_correct.append(common_name)
            print(f"  ✓ CORRECT (#{i+1} prediction: {pred['label']}, confidence: {pred['confidence']:.2%})")
            match_found = True
            break

    if not match_found:
        verified_wrong.append({
            'species': common_name,
            'scientific': scientific_name,
            'top_prediction': predictions[0]['label'],
            'confidence': predictions[0]['confidence'],
            'all_predictions': [p['label'] for p in predictions[:5]]
        })
        print(f"  ❌ WRONG - Model predicts: {predictions[0]['label']} ({predictions[0]['confidence']:.2%})")
        print(f"     Top 5: {', '.join([p['label'] for p in predictions[:5]])}")

    print()
    time.sleep(0.3)  # Rate limiting

# Summary
print()
print("="*80)
print("VERIFICATION RESULTS")
print("="*80)
print()
print(f"✓ Verified Correct: {len(verified_correct)}/{len(species_data)}")
print(f"❌ Verified Wrong: {len(verified_wrong)}/{len(species_data)}")
print(f"⚠️  Could Not Verify: {len(could_not_verify)}/{len(species_data)}")
print()

if verified_correct:
    print(f"CORRECT PHOTOS ({len(verified_correct)}):")
    for name in verified_correct[:20]:
        print(f"  ✓ {name}")
    if len(verified_correct) > 20:
        print(f"  ... and {len(verified_correct) - 20} more")
    print()

if verified_wrong:
    print(f"INCORRECT PHOTOS ({len(verified_wrong)}):")
    print()
    for item in verified_wrong[:10]:
        print(f"  • {item['species']} ({item['scientific']})")
        print(f"    Model predicts: {item['top_prediction']} ({item['confidence']:.2%})")
    if len(verified_wrong) > 10:
        print(f"  ... and {len(verified_wrong) - 10} more")
    print()

if could_not_verify:
    print(f"Could not verify ({len(could_not_verify)}): {', '.join(could_not_verify[:10])}{'...' if len(could_not_verify) > 10 else ''}")
    print()

# Save results
results = {
    'model': model_name,
    'verified_correct': verified_correct,
    'verified_wrong': verified_wrong,
    'could_not_verify': could_not_verify,
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
}

with open('photo_verification_results_v2.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Results saved to: photo_verification_results_v2.json")
print("="*80)
