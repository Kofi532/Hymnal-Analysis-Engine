import os
import json
import django
import pandas as pd

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HymnProject.settings')
django.setup()

from analytics.models import MelodicTransition

def run_import():
    # 1. Load the JSON file
    if not os.path.exists('hymns_c_major.json'):
        print("Error: hymns_c_major.json not found in this directory!")
        return

    with open('hymns_c_major.json', 'r') as f:
        hymns_data = json.load(f)

    # 2. Extract transitions (Soprano/Highest note)
    all_transitions = []
    for hymn in hymns_data:
        # Extract the note name (e.g., 'E4') from "E4 2.0" strings
        notes = []
        for chord in hymn.get('Notes', []):
            if chord:
                # Get the first note in the chord (usually Soprano)
                note_name = chord[0].split()[0] 
                notes.append(note_name)
        
        # Create pairs: (current, next)
        for i in range(len(notes) - 1):
            all_transitions.append((notes[i], notes[i+1]))

    # 3. Calculate Statistics using Pandas
    df = pd.DataFrame(all_transitions, columns=['Current', 'Next'])
    
    # Count specific pairs (e.g., E4 -> D4)
    pair_counts = df.groupby(['Current', 'Next']).size().reset_index(name='PairCount')
    
    # Count total occurrences of each 'Current' note
    totals = df.groupby('Current').size().reset_index(name='Total')
    
    # Merge to calculate probability
    final_df = pd.merge(pair_counts, totals, on='Current')
    final_df['Prob'] = (final_df['PairCount'] / final_df['Total']) * 100

    # 4. Clear the database and Bulk Insert
    print("Clearing old data and importing new stats...")
    MelodicTransition.objects.all().delete()
    
    entries = [
        MelodicTransition(
            current_note=row['Current'],
            next_note=row['Next'],
            pair_count=row['PairCount'],
            total_occurrences=row['Total'],
            probability=row['Prob']
        ) for _, row in final_df.iterrows()
    ]
    
    MelodicTransition.objects.bulk_create(entries)
    print(f"Successfully imported {len(entries)} melodic transitions!")

if __name__ == "__main__":
    run_import()