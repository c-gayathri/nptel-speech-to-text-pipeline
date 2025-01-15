#!/bin/bash

# Bash script for audio preprocessing with parallelization
# Usage: ./preprocess_audio.sh <input_directory_path> <output_directory_path> <num_cpus>

# Input validation
if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <input_directory_path> <output_directory_path> <num_cpus>"
  exit 1
fi

INPUT_DIR_PATH=$1
OUTPUT_DIR_PATH=$2
NUM_CPUS=$3

# Check if input directory exists
if [ ! -d "$INPUT_DIR_PATH" ]; then
  echo "Error: Input directory $INPUT_DIR_PATH does not exist!"
  exit 1
fi

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR_PATH"

# Function to process a single file
process_audio() {
  local input_file=$1
  local output_file=$2
  # Convert the audio to 16kHz mono without clipping
  ffmpeg -y -i "$input_file" -ar 16000 -ac 1 "$output_file"
}

export -f process_audio

# Check for audio files in the input directory
audio_files=$(find "$INPUT_DIR_PATH" -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.m4a" \))

if [ -z "$audio_files" ]; then
  echo "No audio files found in the input directory: $INPUT_DIR_PATH"
  exit 1
else
  echo "Found the following audio files:"
  echo "$audio_files"
fi

# Process audio files in parallel
echo "Processing audio files..."
echo "$audio_files" | parallel -j "$NUM_CPUS" process_audio {} "$OUTPUT_DIR_PATH/{/.}.wav"

echo "Audio preprocessing completed!"
