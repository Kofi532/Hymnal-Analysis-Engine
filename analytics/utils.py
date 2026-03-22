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
import numpy as np
import json
from music21 import pitch, chord

def get_analytical_df(json_path):
    """
    Processes hymn data and extracts musical features.
    Optimized to minimize memory usage by destroying music21 objects 
    immediately after extraction.
    """
    try:
        with open(json_path, 'r') as f:
            hymns_data = json.load(f)
    except FileNotFoundError:
        return pd.DataFrame()

    all_chords = []
    
    for hymn in hymns_data:
        hymn_id = hymn.get('title', 'Unknown')
        # Process each chord sequence in the hymn
        for idx, chord_notes in enumerate(hymn.get('Notes', [])):
            if not chord_notes: 
                continue
            
            # 1. Create temporary pitch objects for sorting/analysis
            temp_pitches = []
            for n_str in chord_notes:
                try:
                    # Extracts note name (e.g., 'C4' from 'C4 1.0')
                    p_name = n_str.split()[0]
                    temp_pitches.append(pitch.Pitch(p_name))
                except (IndexError, ValueError):
                    continue
            
            if not temp_pitches: 
                continue

            # 2. Sort by pitch height (Soprano at index 0)
            temp_pitches.sort(key=lambda x: x.ps, reverse=True)
            
            # 3. Extract the primitives (strings/floats) we actually need
            soprano_note = temp_pitches[0].nameWithOctave
            soprano_ps = temp_pitches[0].ps
            
            # 4. Briefly create a Chord object for the consonance check
            # Then let it be garbage collected to save RAM
            c_obj = chord.Chord(temp_pitches)
            is_consonant = c_obj.isConsonant()
            
            # 5. Store only lightweight data types in the main list
            all_chords.append({
                'hymn_id': hymn_id,
                'chord_idx': idx,
                'soprano_note': soprano_note,
                'soprano_ps': soprano_ps,
                'is_consonant': is_consonant
            })
            
            # Explicitly clear the heavy objects from this iteration
            del c_obj
            del temp_pitches

    return pd.DataFrame(all_chords)

def generate_markov_data(df):
    """
    Generates a transition probability matrix for the Soprano line.
    """
    if df.empty or 'soprano_note' not in df.columns:
        return {}

    # Calculate transitions: what note follows the current one?
    transitions = pd.DataFrame({
        'current': df['soprano_note'], 
        'next': df['soprano_note'].shift(-1)
    }).dropna()
    
    # Create the probability matrix (normalized by row)
    matrix = pd.crosstab(
        transitions['current'], 
        transitions['next'], 
        normalize='index'
    )
    
    return matrix.to_dict(orient='index')

def get_raw_json_df(json_path):
    """
    Provides a simplified DataFrame for raw data display.
    """
    try:
        with open(json_path, 'r') as f:
            hymns_data = json.load(f)
    except FileNotFoundError:
        return pd.DataFrame()
    
    raw_rows = []
    for hymn in hymns_data:
        hymn_id = hymn.get('title', 'Unknown')
        for idx, chord_notes in enumerate(hymn.get('Notes', [])):
            raw_rows.append({
                'hymn_id': hymn_id,
                'chord_idx': idx,
                'raw_notes': ", ".join(chord_notes) if chord_notes else "REST"
            })
            
    return pd.DataFrame(raw_rows)