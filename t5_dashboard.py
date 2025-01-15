import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import json
import sys
import os

# Ensure the JSONL file is provided as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python app.py <path_to_jsonl_file>")
    sys.exit(1)

jsonl_file = sys.argv[1]

if not os.path.isfile(jsonl_file):
    print(f"Error: The file {jsonl_file} does not exist.")
    sys.exit(1)

# Read the JSONL file and convert it to a pandas DataFrame
data = []
try:
    with open(jsonl_file, 'r') as file:
        for line in file:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"Warning: Skipping malformed JSON line in {jsonl_file}")
except Exception as e:
    print(f"Error reading JSONL file: {e}")
    sys.exit(1)

# Check if data is empty
if not data:
    print(f"Error: The data from {jsonl_file} is empty.")
    sys.exit(1)

# Convert the list of JSON objects to a DataFrame
df = pd.DataFrame(data[1:])

# Add derived columns
df['duration_minutes'] = df['duration'] / 60

# Create Dash app
app = dash.Dash(__name__)

num_files = len(data) -1

# Obtain the aggregate numbers to be used for display
total_dur_seconds = data[0]["aggregates"]["total duration in seconds"]
total_dur_hours = data[0]["aggregates"]["total duration in hours"]
vocab_size = data[0]["aggregates"]["vocabulary size"]
alphabet_size = data[0]["aggregates"]["alphabet size"]
alphabet = data[0]["aggregates"]["alphabet"]
vocabulary = data[0]["aggregates"]["vocabulary"]
total_segments = data[0]["aggregates"]["total number of segments"]
avg_segment_dur = data[0]["aggregates"]["average segment duration"]

# Generate the string of alphabets to be displayed
alphabet_print = ""
for character in alphabet[:-1]:
    alphabet_print += character + ", " 
alphabet_print += alphabet[-1]

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Audio Statistics Visualization"),

    # Display the aggregate statistics
    html.Div([
        html.H3("Global Statistics"),
        html.Div([
            html.P(f"Total number of audio files: {num_files}"),
            html.P(f"Total Duration: {total_dur_seconds:.0f} seconds ({total_dur_hours:.2f} hours)"),
            html.P(f"Vocabulary size: {vocab_size} words"),
            html.P(f"Alphabet size: {alphabet_size} characters"),
            html.P(f"Alphabet: {alphabet_print}"),
            html.P(f"Total number of segments: {total_segments}"),
            html.P(f"Average duration of segments: {avg_segment_dur}"),
        ]),
    ]),

    # Graphs to visualize duration, number of words, number of characters, number of segments, and average duration of segments
    html.Div([
        dcc.Graph(
            id='duration_histogram',
            figure=px.histogram(df, x='duration', nbins=20, title="Duration per Audio File (Seconds)").update_layout(xaxis_title="Duration (Seconds)", yaxis_title="Number of audio files")
        ),
        dcc.Graph(
            id='words_histogram',
            figure=px.histogram(df, x='num_words', nbins= 20, title="Number of Words per Audio File").update_layout(xaxis_title="Number of words", yaxis_title="Number of audio files")
        ),
        dcc.Graph(
            
            id='characters_histogram',
            figure=px.histogram(df, x='num_char', nbins=20, title="Number of Characters per Audio File").update_layout(xaxis_title="Number of characters", yaxis_title="Number of audio files")
        ),
        dcc.Graph(
            id='segments_histogram',
            figure=px.histogram(df, x='num_segments', nbins=20, title="Number of Segments per Audio File").update_layout(xaxis_title="Number of segements", yaxis_title="Number of audio files")
        ),
        dcc.Graph(
            id='segments_dur_histogram',
            figure=px.histogram(df, x='avg_segment_dur', nbins=20, title="Average Duration of Segments per Audio File").update_layout(xaxis_title="Average duration (seconds)", yaxis_title="Number of audio files")
        ),
    ]),
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
