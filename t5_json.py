import librosa
import soundfile as sf
import os
import json

# Load the audio file
def update_json(json_path, output_file):
    try:
        with open(json_path, 'r') as file:
            data = []
            for line in file:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON on line {file.tell()}: {e}")
                    continue
    except FileNotFoundError:
        print(f"Error: The file {json_path} was not found.")
        return
    except IOError as e:
        print(f"Error reading the file {json_path}: {e}")
        return

    vocabulary = set()
    alphabet = set()
    total_duration = 0
    total_segments = 0
    total_segment_dur = 0

    for i,entry in enumerate(data):
        audio_path = entry['audio_filepath'] 

        if not audio_path or not os.path.exists(audio_path):
            print(f"Warning: Audio file {audio_path} not found for entry {i}")
            continue

        try:
            y, sr = librosa.load(audio_path, sr=None)  # sr=None to preserve the original sampling rate
        except Exception as e:
            print(f"Error loading audio file {audio_path}: {e}")
            continue

        intervals = librosa.effects.split(y, top_db=20)
        segment_durations = [(end-start)/sr for start,end in intervals]

        # Update the json entry with new data fields for number of characters and words
        split_text = entry["text"].split()
        data[i]["num_words"] = len(split_text)
        data[i]["num_char"] = len(entry["text"])
        
        # Add to the global vocabulary and alphabet
        entry_vocab = set(split_text)
        vocabulary.update(entry_vocab)
        entry_alphabet = set(entry["text"])
        alphabet.update(entry_alphabet)

        # add to global segment calculation
        total_segment_dur += sum(segment_durations)
        total_segments += len(segment_durations)

        # Update the json entry with new data fields for segment information
        data[i]["num_segments"] = len(intervals)
        if len(intervals) > 0:
            data[i]["avg_segment_dur"] = sum(segment_durations) / len(segment_durations)
        else:
            data[i]["avg_segment_dur"] = 0


        total_duration += data[i]["duration"]

    aggregates = {
        "vocabulary": list(vocabulary),
        "vocabulary size": len(vocabulary),
        "alphabet size": len(alphabet),
        "alphabet": list(alphabet),
        "total duration in seconds": total_duration,
        "total duration in hours": total_duration/(60*60),
        "total number of segments": total_segments,
        "average segment duration": total_segment_dur/total_segments,
    }
    

    try:
        with open(output_file, "w") as f:
            if len(data) == 0:
                print("Error: No entries were generated")
            
            json.dump({"aggregates": aggregates}, f, ensure_ascii=False)
            f.write("\n")
            for entry in data:
                # print(entry)
                json.dump(entry, f, ensure_ascii=False)
                f.write("\n")

    except IOError as e:
        print(f"Error writing to {output_file}: {e}")


if __name__ == "__main__":
    import argparse

    # Argument parser for command-line usage
    parser = argparse.ArgumentParser(description="Update json to include new data metrics.")
    parser.add_argument("json_path", help="File containing json to be updated.")
    parser.add_argument("output_file", help="Path to save new json file.")
    args = parser.parse_args()

    # Process PDFs
    update_json(args.json_path, args.output_file)