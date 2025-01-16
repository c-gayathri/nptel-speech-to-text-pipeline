import os
import sys
import numpy as np
import librosa
import soundfile as sf

def segment_audio(file_path):
    # Load audio file
    y, sr = librosa.load(file_path, sr=None)
    
    # Compute energy of the audio signal
    energy = np.array([np.sum(np.abs(y[i:i + 2048] ** 2)) for i in range(0, len(y), 2048)])
    
    # Define a threshold for energy to identify segments (this can be adjusted)
    threshold = np.mean(energy) * 0.25
    
    # Identify segments based on energy threshold
    segments = []
    start = None
    
    for i, e in enumerate(energy):
        if e > threshold:
            if start is None:
                start = i * 2048 / sr  # Convert to seconds
        else:
            if start is not None:
                end = i * 2048 / sr  # Convert to seconds
                segments.append((start, end))
                start = None
    
    # Check if there's an ongoing segment at the end of the file
    if start is not None:
        end = len(y) / sr  # End at the last sample
        segments.append((start, end))
    
    return segments

def clip_audio(y, sr, start_time, duration_to_remove):
    start_sample = int(start_time * sr)
    end_sample = len(y)  # Clip until the end of the audio
    new_end_sample = max(start_sample, end_sample - int(duration_to_remove * sr))
    return y[start_sample:new_end_sample]

def process_directory(input_dir):
    all_segments_info = []
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.wav'):
            file_path = os.path.join(input_dir, filename)
            segments = segment_audio(file_path)
            
            if segments:
                # Get start time of first segment and calculate last segment duration
                first_segment_start = segments[1][0]
                last_segment_end = segments[-2][1]
                total_duration = len(librosa.load(file_path, sr=None)[0]) / librosa.get_samplerate(file_path)
                last_segment_duration = total_duration - last_segment_end
                
                all_segments_info.append((first_segment_start, last_segment_duration))
    
    return all_segments_info

def main(input_dir, output_dir, manual_start=None, manual_duration=None):
    if manual_start is not None and manual_duration is not None:
        avg_start_time = manual_start
        avg_last_segment_duration = manual_duration
        print(f"Using Manual Start Time: {avg_start_time:.2f} seconds")
        print(f"Using Manual Last Segment Duration: {avg_last_segment_duration:.2f} seconds")
    else:
        all_segments_info = process_directory(input_dir)

        if not all_segments_info:
            print("No valid audio files found.")
            return

        # Calculate averages
        avg_start_time = np.mean([info[0] for info in all_segments_info])
        avg_last_segment_duration = np.mean([info[1] for info in all_segments_info])

        print(f"Average Start Time: {avg_start_time:.2f} seconds")
        print(f"Average Last Segment Duration: {avg_last_segment_duration:.2f} seconds")

    # Now clip each audio file based on provided or calculated values
    for filename in os.listdir(input_dir):
        if filename.endswith('.wav'):
            file_path = os.path.join(input_dir, filename)
            y, sr = librosa.load(file_path, sr=None)

            # Clip from average or manual values
            clipped_audio = clip_audio(y, sr, avg_start_time, avg_last_segment_duration)

            # Save clipped audio to output directory
            os.makedirs(output_dir, exist_ok=True)
            output_file_path = os.path.join(output_dir, f"clipped_{filename}")
            sf.write(output_file_path, clipped_audio, sr)

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print("Usage: python segment_audio.py <input_directory> <output_directory> [<start_time> <last_segment_duration>]")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]

    manual_start_time = float(sys.argv[3]) if len(sys.argv) == 5 else None
    manual_last_segment_duration = float(sys.argv[4]) if len(sys.argv) == 5 else None

    main(input_directory, output_directory, manual_start=manual_start_time, manual_duration=manual_last_segment_duration)
