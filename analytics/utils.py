import pandas as pd
import numpy as np
import json
from music21 import pitch, chord

def get_analytical_df(json_path):
    with open(json_path, 'r') as f:
        hymns_data = json.load(f)
    
    all_chords = []
    for hymn in hymns_data:
        hymn_id = hymn['title']
        for idx, chord_notes in enumerate(hymn['Notes']):
            if not chord_notes: continue
            
            m21_notes = []
            for n_str in chord_notes:
                try:
                    p_name, _ = n_str.split()
                    m21_notes.append(pitch.Pitch(p_name))
                except: continue
            
            # Sort by pitch height: Soprano is index 0
            m21_notes.sort(key=lambda x: x.ps, reverse=True)
            if not m21_notes: continue

            all_chords.append({
                'hymn_id': hymn_id,
                'chord_idx': idx,
                'soprano_note': m21_notes[0].nameWithOctave,
                'soprano_ps': m21_notes[0].ps,
                'is_consonant': chord.Chord(m21_notes).isConsonant()
            })
    return pd.DataFrame(all_chords)

def generate_markov_data(df):
    # Calculate transitions for the Soprano voice
    transitions = pd.DataFrame({
        'current': df['soprano_note'], 
        'next': df['soprano_note'].shift(-1)
    }).dropna()
    
    # Create the probability matrix
    matrix = pd.crosstab(transitions['current'], transitions['next'], normalize='index')
    return matrix.to_dict(orient='index')



def get_raw_json_df(json_path):
    with open(json_path, 'r') as f:
        hymns_data = json.load(f)
    
    raw_rows = []
    for hymn in hymns_data:
        hymn_id = hymn['title']
        for idx, chord_notes in enumerate(hymn['Notes']):
            # Join notes into a string to display them in a single table cell
            raw_rows.append({
                'hymn_id': hymn_id,
                'chord_idx': idx,
                'raw_notes': ", ".join(chord_notes) if chord_notes else "REST"
            })
    return pd.DataFrame(raw_rows)