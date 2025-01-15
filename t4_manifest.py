import os
import json
import soundfile as sf
import re
import argparse

def read_txt_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: The file {file_path} is not found")
    except Exception as e:
        print(f"Error: {e}")
    
def get_audio_duration(file_path):
    try:
        with sf.SoundFile(file_path) as audio:
            return len(audio) / audio.samplerate
    except Exception as e:
        print(f"Error: Could not get duration for {file_path} - {e}")  # Detailed error for audio processing
        return None

def write_json(audio_dir, text_dir, file_name = "train_manifest.jsonl"):

    if not os.path.isdir(audio_dir):
        print(f"Error: {audio_dir} does not exist or is not a directory")
        return
    if not os.path.isdir(text_dir):
        print(f"Error: {text_dir} does not exist or is not a directory")
        return

    manifest_data = []

    for audio_file in os.listdir(audio_dir):
        if not audio_file.endswith(".wav") or not re.match(r"mod(\d+)lec(\d+).wav", audio_file):
            print("Error: The file " + audio_file + " is not in the desired format")
            continue

        lec_num = int(re.match(r"mod(\d+)lec(\d+).wav", audio_file).group(2))
        text_file = "lec" + str(lec_num) + ".txt"
        text_filepath = os.path.join(text_dir, text_file)
        transcription = read_txt_file(text_filepath)

        if read_txt_file(text_filepath) == None:
            continue
        audio_filepath = os.path.join(audio_dir,audio_file)
        duration = get_audio_duration(audio_filepath)

        entry = {
            "audio_filepath": audio_filepath,
            "duration": duration,
            "text": transcription
        }

        manifest_data.append(entry)


    try:
        with open(file_name, "w") as f:
            if len(manifest_data) == 0:
                print("Error: No entries were generated")
            for entry in manifest_data:
                json.dump(entry, f, ensure_ascii=False)
                f.write("\n")
    except Exception as e:
        print(f"Error: Failed to write manifest to {file_name} - {e}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Prepare a traiing manifest file from audio directory and .txt files.")
    parser.add_argument("audio_dir", help="Directory containing audio files.")
    parser.add_argument("text_dir", help="Directory containing text files.")
    parser.add_argument("file_name", help="File name to save the training manifest data (.jsonl).")
    args = parser.parse_args()

    write_json(args.audio_dir, args.text_dir, args.file_name)
