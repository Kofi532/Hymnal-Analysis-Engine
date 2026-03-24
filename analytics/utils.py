# import pandas as pd
# import numpy as np
# import json
# from music21 import pitch, chord

# def get_analytical_df(json_path):
#     with open(json_path, 'r') as f:
#         hymns_data = json.load(f)
    
#     all_chords = []
#     for hymn in hymns_data:
#         hymn_id = hymn['title']
#         for idx, chord_notes in enumerate(hymn['Notes']):
#             if not chord_notes: continue
            
#             m21_notes = []
#             for n_str in chord_notes:
#                 try:
#                     p_name, _ = n_str.split()
#                     m21_notes.append(pitch.Pitch(p_name))
#                 except: continue
            
#             # Sort by pitch height: Soprano is index 0
#             m21_notes.sort(key=lambda x: x.ps, reverse=True)
#             if not m21_notes: continue

#             all_chords.append({
#                 'hymn_id': hymn_id,
#                 'chord_idx': idx,
#                 'soprano_note': m21_notes[0].nameWithOctave,
#                 'soprano_ps': m21_notes[0].ps,
#                 'is_consonant': chord.Chord(m21_notes).isConsonant()
#             })
#     return pd.DataFrame(all_chords)

# def generate_markov_data(df):
#     # Calculate transitions for the Soprano voice
#     transitions = pd.DataFrame({
#         'current': df['soprano_note'], 
#         'next': df['soprano_note'].shift(-1)
#     }).dropna()
    
#     # Create the probability matrix
#     matrix = pd.crosstab(transitions['current'], transitions['next'], normalize='index')
#     return matrix.to_dict(orient='index')



# def get_raw_json_df(json_path):
#     with open(json_path, 'r') as f:
#         hymns_data = json.load(f)
    
#     raw_rows = []
#     for hymn in hymns_data:
#         hymn_id = hymn['title']
#         for idx, chord_notes in enumerate(hymn['Notes']):
#             # Join notes into a string to display them in a single table cell
#             raw_rows.append({
#                 'hymn_id': hymn_id,
#                 'chord_idx': idx,
#                 'raw_notes': ", ".join(chord_notes) if chord_notes else "REST"
#             })
#     return pd.DataFrame(raw_rows)

import pandas as pd
import json

def get_analytical_df(json_path):
    """
    Processes the pre-analyzed JSON containing MIDI numbers.
    Bypasses music21 for maximum speed and efficiency.
    """
    try:
        with open(json_path, 'r') as f:
            hymns_data = json.load(f)
    except FileNotFoundError:
        print("File not found. Please ensure the JSON is uploaded.")
        return pd.DataFrame()

    # Helper function to convert MIDI number back to a Note Name (optional/convenience)
    def midi_to_name(n):
        names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (n // 12) - 1
        name = names[n % 12]
        return f"{name}{octave}"

    all_chords = []
    
    for entry in hymns_data:
        midi_list = entry.get('midi_numbers', [])
        
        if not midi_list:
            continue
            
        # 1. Identify Soprano (The highest MIDI number)
        # We sort the midi list descending; index 0 is the highest pitch
        sorted_midi = sorted(midi_list, reverse=True)
        soprano_midi = sorted_midi[0]
        
        all_chords.append({
            'hymn_id': entry.get('hymn_id'),
            'chord_idx': entry.get('chord_idx'),
            'soprano_note': midi_to_name(soprano_midi),
            'soprano_ps': float(soprano_midi), # 'ps' in music21 is equivalent to MIDI number
            'is_consonant': entry.get('is_consonant')
        })
        
    return pd.DataFrame(all_chords)

def generate_markov_data(df):
    """
    Generates transition probability matrix for the Soprano line.
    """
    if df.empty: return {}

    transitions = pd.DataFrame({
        'current': df['soprano_note'], 
        'next': df['soprano_note'].shift(-1)
    }).dropna()
    
    matrix = pd.crosstab(
        transitions['current'], 
        transitions['next'], 
        normalize='index'
    )
    return matrix.to_dict(orient='index')



import pandas as pd
import json

def get_raw_json_df(json_path):
    """
    Produces the raw data table using the pre-analyzed JSON file.
    This version is highly efficient as the data is already flattened.
    """
    try:
        with open(json_path, 'r') as f:
            hymns_data = json.load(f)
    except FileNotFoundError:
        print("File not found.")
        return pd.DataFrame()
    
    # Since your new JSON is already a list of chord-level dictionaries,
    # pandas can load it directly. We just select the columns we want.
    df = pd.DataFrame(hymns_data)
    
    # Ensure we return only the specific columns requested in the original function
    # but using the keys present in your new file
    if not df.empty:
        return df[['hymn_id', 'chord_idx', 'raw_notes']]
    
