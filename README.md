# NPTEL Course Downloader and Audio Processing Pipeline

This project provides a comprehensive pipeline for downloading NPTEL (National Programme on Technology Enhanced Learning) course materials, processing audio files, and generating training data for machine learning models.

The pipeline consists of several scripts that work together to download course transcripts and lecture videos, preprocess audio files, extract text from PDFs, generate training manifests, and visualize audio statistics. This toolset is designed for researchers and developers working on speech recognition or natural language processing tasks using NPTEL course data.

## Repository Structure

```
.
├── README.md
├── t1_downloader.py
├── t2_wav.sh
├── t3_txt.py
├── t4_manifest.py
├── t5_dashboard.py
└── t5_json.py
└── train_manifest.jsonl
└── updated_data.jsonl
```

- `t1_downloader.py`: Downloads course transcripts and lecture videos from NPTEL website.
- `t2_wav.sh`: Bash script for audio preprocessing with parallelization.
- `t3_txt.py`: Extracts and processes text from PDF files.
- `t4_manifest.py`: Generates a training manifest file in JSONL format.
- `t5_dashboard.py`: Creates a Dash application to visualize audio statistics.
- `t5_json.py`: Updates JSON files with additional audio metadata.

## Usage Instructions

### Installation

1. Clone the repository:
   ```
   git clone <repository_url>
   cd <repository_name>
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt   
   ```

3. Install FFmpeg for audio processing:
   - On Ubuntu: `sudo apt-get install ffmpeg`
   - On macOS with Homebrew: `brew install ffmpeg`

### Downloading Course Materials

To download course materials, use the `t1_downloader.py` script:

```
python t1_downloader.py <course_url> <output_directory> <download_type>
```

The value of download_type corresponds to the following:
- "-t": only transcripts
- "-l": only lectures
- "-tl": both transscripts and lectures (default)

Example:
```
python t1_downloader.py https://nptel.ac.in/courses/106106184 downloads/106106184 -tl
```

### Audio Preprocessing

To preprocess audio files, that is, converting the downloaded .mp3 files to .wav files, use the `t2_wav.sh` script:

```
bash t2_wav.sh <input_directory_path> <output_directory_path> <num_cpus>

# Example:
bash t2_wav.sh downloads/106106184/lectures wav_files/106106184 4

```

### Text Extraction from PDFs

To extract text from PDF files, use the `t3_txt.py` script:

```
python t3_txt.py <input_directory> <output_directory>

# Example:
python t3_txt.py downloads/106106184/transcripts txtfiles/106106184
```

### Generating Training Manifest

To create a training manifest file, use the `t4_manifest.py` script:

```
python t4_manifest.py <audio_directory> <text_directory> <output_file.jsonl>

# Example:
python t4_manifest.py wav_files/106106184/ txtfiles/106106184/ train_manifest.jsonl
```

### Updating JSON with Audio Metadata

To update JSON files with additional audio metadata, use the `t5_json.py` script:

```
python t5_json.py <input_json_file> <output_json_file>

# Example:
python t5_json.py train_manifest.jsonl updated_data.jsonl
```

### Visualizing Audio Statistics

To visualize audio statistics, use the `t5_dashboard.py` script:

```
python t5_dashboard.py <path_to_jsonl_file>

# Example:
python t5_dashboard.py updated_data.jsonl
```

The dashboard is hosted locally and can be viewed by following this address: [http://127.0.0.1:8050/](http://127.0.0.1:8050/)

## Data Flow

1. Course materials are downloaded using `t1_downloader.py` in the folder '<download_dir>'. The .mp3 lecture audio files are saved in '<download_dir>/lectures' and the .pdf transcript files are saved in '<download_dir>/transcripts'.
2. Audio .mp3 files in '<download_dir>/lectures' are preprocessed using `t2_wav.sh` and are converted into .wav files and stored in '<wav_dir>'.
3. Text is extracted from PDFs in '<download_dir>/transcripts' using `t3_txt.py` and stored in .txt files in '<txt_dir>'.
4. A training manifest JSON file is generated using `t4_manifest.py` and stored in '<manifest_file>'.
    - Input:
5. Audio statistics are visualized using `t5_dashboard.py`.
6. JSON files are updated with additional metadata using `t5_json.py`.

```
[Course Website] -> t1_downloader.py -> [Raw Audio Files]
[Raw Audio Files] -> t2_wav.sh -> [Preprocessed Audio]
[PDF Transcripts] -> t3_txt.py -> [Extracted Text]
[Preprocessed Audio] + [Extracted Text] -> t4_manifest.py -> [Training Manifest]
[Training Manifest] -> t5_dashboard.py -> [Visualization]
[Training Manifest] -> t5_json.py -> [Updated JSON with Metadata]
```

## Troubleshooting

- If `t1_downloader.py` fails to interact with web elements, try increasing the wait time in the `WebDriverWait` constructor.
- For audio processing issues in `t2_wav.sh`, ensure FFmpeg is correctly installed and accessible in your system's PATH.
- If text extraction fails in `t3_txt.py`, check if the PDF files are not password-protected or corrupted.
- For manifest generation issues in `t4_manifest.py`, verify that the audio files and corresponding text files have matching names.
- If the dashboard in `t5_dashboard.py` doesn't load, check if the JSONL file path is correct and the file is not empty.