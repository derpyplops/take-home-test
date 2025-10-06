import csv
import json

# Get human annotations
human_intents = {}
with open('data/dataset.csv', 'r') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader, 1):
        human_intents[i] = row['human_generated_intent']

# Load our results
with open('full_results.json', 'r') as f:
    results = json.load(f)

# Find mismatches and show transcripts
mismatches = []
for result in results['results']:
    idx = result['transcript_index']
    predicted = result['intent']
    human = human_intents[idx]
    transcript = result['transcript']
    
    if predicted != human:
        mismatches.append((idx, human, predicted, transcript))

print('=== EXAMINING WRONGLY CLASSIFIED EXAMPLES ===')
print()

# Look at first 5 mismatches in detail
for idx, human, predicted, transcript in mismatches[:5]:
    print(f'Example #{idx}:')
    print(f'Human: {human}')
    print(f'GPT-5: {predicted}')
    print('Transcript excerpt:')
    # Show first 500 chars of transcript
    print(f'{transcript[:500]}...')
    print('-' * 80)