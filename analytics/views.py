from django.shortcuts import render
from django.core.paginator import Paginator
from .utils import get_analytical_df, generate_markov_data, get_raw_json_df
# from .utils import get_analytical_df
import os
from django.conf import settings
from django.core.paginator import Paginator
import json 

def raw_data_table(request):
    json_path = os.path.join(settings.BASE_DIR, 'hymns_with_midi.json')
    df = get_analytical_df(json_path)
    
    # Pagination: 50 rows per page to handle 50,000+ instances efficiently
    data_list = df.to_dict('records')
    paginator = Paginator(data_list, 50) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'analytics/data_table.html', {'page_obj': page_obj})







def dashboard_(request):
    json_path = os.path.join(settings.BASE_DIR, 'hymns_with_midi.json')
    df = get_analytical_df(json_path)
    
    # Get Markov probabilities for the chart
    # We will take a slice of the most frequent transitions for visualization
    markov_dict = generate_markov_data(df)
    
    # Pick a sample note to display (e.g., C4 or the most common note)
    sample_note = df['soprano_note'].mode()[0]
    sample_transitions = markov_dict.get(sample_note, {})
    
    # Prepare data for Chart.js
    chart_labels = list(sample_transitions.keys())
    chart_data = [round(v * 100, 2) for v in sample_transitions.values()]

    context = {
        'total_transitions': len(df),
        'consonance_rate': round(df['is_consonant'].mean() * 100, 2),
        'unique_hymns': df['hymn_id'].nunique(),
        'top_start_note': sample_note,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'analytics/dashboard.html', context)




    

def raw_data_table(request):
    json_path = os.path.join(settings.BASE_DIR, 'hymns_with_midi.json')
    df = get_analytical_df(json_path)
    
    # Convert DataFrame to list of dictionaries for Django templates
    data_list = df.to_dict('records')
    
    # Show 50 rows per page
    paginator = Paginator(data_list, 50) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'analytics/data_table.html', {'page_obj': page_obj})



def raw_json_table(request):
    json_path = os.path.join(settings.BASE_DIR, 'hymns_with_midi.json')
    df = get_raw_json_df(json_path) # Uses the new function
    
    paginator = Paginator(df.to_dict('records'), 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'analytics/raw_json_table.html', {'page_obj': page_obj})




    

def dashboard(request):
    json_path = os.path.join(settings.BASE_DIR, 'hymns_with_midi.json')
    df = get_analytical_df(json_path)
    
    # 1. Get the full Markov Dictionary { 'C4': {'D4': 0.2, 'E4': 0.1}, ... }
    markov_dict = generate_markov_data(df)
    
    # 2. Identify all available notes for the dropdown
    available_notes = sorted(markov_dict.keys())
    
    # 3. Default note for initial page load
    default_note = "E4" if "E4" in available_notes else available_notes[0]
    
    context = {
        'total_transitions': len(df),
        'consonance_rate': round(df['is_consonant'].mean() * 100, 2),
        'unique_hymns': df['hymn_id'].nunique(),
        'top_start_note': default_note,
        'available_notes': available_notes,
        # We pass the full matrix as a JSON string for JavaScript to use
        'full_matrix_json': json.dumps(markov_dict), 
    }
    return render(request, 'analytics/dashboard.html', context)