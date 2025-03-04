# NPTEL Course Downloader and Audio Processing Pipeline

This project provides a comprehensive pipeline for downloading NPTEL (National Programme on Technology Enhanced Learning) course materials, processing audio files, and generating training data for machine learning models.

The pipeline consists of several scripts that work together to download course transcripts and lecture videos, preprocess audio files, extract text from PDFs, generate training manifests, and visualize audio statistics. 

## Repository Structure

```
.
├── README.md
├── t1_downloader.py
├── t2_process.py
├── t2_wav.sh
├── t3_txt.py
├── t4_manifest.py
├── t5_dashboard.py
└── t5_json.py
└── train_manifest.jsonl
└── updated_data.jsonl
```

- `t1_downloader.py`: Downloads course transcripts and lecture audios from NPTEL website.
- 't2_process.py': Preprocesses audio files to clip segments with music.
- `t2_wav.sh`: Bash script for audio conversion into .wav with parallelization.
- `t3_txt.py`: Extracts and processes text from PDF files.
- `t4_manifest.py`: Generates a training manifest file in JSONL format.
- `t5_dashboard.py`: Creates a Dash application to visualize audio statistics.
- `t5_json.py`: Updates JSON files with additional audio metadata.
- `train_manifest.jsonl`: Contains the manifest data for training.
- `updated_data.jsonl`: Contains additional metrics that are helpful for visualisation

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

To download course materials (audio of lectures and trasncript PDFs), use the `t1_downloader.py` script:

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
bash t2_wav.sh <input_directory_path> <wav_files_directory> <num_cpus>

python t2_process.py <wav_files_directory> <output_directory_path> <clip_duration_at_start_in_seconds(optional)> <clip_duration_at_end_in_seconds(optional)>


# Example:

bash t2_wav.sh downloads/106106184/lectures wav_files/106106184 4

python t2_process.py wav_files/106106184/ wav_files_processed_automatic/106106184

python t2_process.py wav_files/106106184/ wav_files_processed_manual/106106184 10 30

```

### Text Extraction from PDFs

To extract text from PDF files and preprocess it, use the `t3_txt.py` script:

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
python t4_manifest.py wav_files_processed_manual/106106184/ txtfiles/106106184/ train_manifest.jsonl
```

### Updating JSON with Audio Metadata

To create a JSON file with additional metrics that is necessary for visualisation, including aggregate statistics, use the `t5_json.py` script:

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
    - Input: <course_url>
    - Output: '<download_dir>/lectures', '<download_dir>/transcripts'
2. Audio .mp3 files in '<download_dir>/lectures' are converted into .wav files using `t2_wav.sh` and stored in '<wav_dir>'.
    - Input: '<download_dir>/lectures'
    - Output: '<wav_dir>'
3. The .wav files in '<wav_dir>' are preprocessed using 't2_process.py'. It clips the audio files at the start and the end to remove the music.
    - Input: '<wav_dir>'
    - Output: '<wav_processed_dir>'
4. Text is extracted from PDFs in '<download_dir>/transcripts' using `t3_txt.py` and stored in .txt files in '<txt_dir>'.
    - Input: '<download_dir>/transcripts'
    - Output: '<txt_dir>'
5. A training manifest JSON file is generated using `t4_manifest.py` and stores information about the .wav and .txt files in '<wav_processed_dir>' and '<txt_dir>' in '<manifest_file>'.
    - Input: '<wav_processed_dir>', '<txt_dir>'
    - Output: '<manifest_file>'
6. JSON file '<manifest_file>' is used to generate a new file '<updated_json_file>' with additional metadata using `t5_json.py`.
    - Input: '<manifest_file>'
    - Output: '<updated_json_file>'
7. Audio statistics in '<updated_json_file>' are visualized using `t5_dashboard.py`.
    - Input: '<updated_json_file>'

## Troubleshooting

- If `t1_downloader.py` fails to interact with web elements, try increasing the wait time in the `WebDriverWait` constructor.
- For audio processing issues in `t2_wav.sh`, ensure FFmpeg is correctly installed and accessible in your system's PATH.
- If text extraction fails in `t3_txt.py`, check if the PDF files are not password-protected or corrupted.
- For manifest generation issues in `t4_manifest.py`, verify that the audio files and corresponding text files have matching names (the lecture numbers should match).
- If the dashboard in `t5_dashboard.py` doesn't load, check if the JSONL file path is correct and the file is not empty.


## Observations

### Task 1

The NPTELDownloader class implements an automated web scraping solution using Selenium WebDriver to interact with NPTEL course pages. It systematically navigates through course content by clicking relevant buttons and handling language dropdowns, collecting download links for both transcripts and lecture videos. The implementation includes robust retry mechanisms for reliability and error handling. The downloader stores the collected links in dictionaries and subsequently downloads transcript files and audio files to a specified folder structure maintaining proper organization. 

The code adapts to different NPTEL course layouts by searching tabs  until it finds the one with the required text ('transcript' or 'videos'). Therefore, it is able to handle different layouts across different courses.

It was tested with the following courses and was able to download the mp3 files and transcript PDFs successfully:
- [NOC:Introduction to Launch Vehicle Analysis and Design, IIT Bombay](https://nptel.ac.in/courses/101101086)
- [NOC:Introduction to Aerospace Engineering, IIT Bombay](https://nptel.ac.in/courses/101101079)

### Task 2

The t2_wav.sh script preprocesses audio files (MP3, WAV, M4A) by converting them to 16kHz mono WAV format using FFmpeg. It processes the files in parallel, optimizing for speed based on the number of CPU cores specified, and handles input validation, error checking, and directory management for efficient batch processing. It automatically searches for any .mp3 and .m4a files in the given directory.

The last few seconds and the first few seconds in every audio file contains music. This needs to be clipped.

The t2_process.py file clips the music at the start and end of each lecture. It has two modes:
- This is trigerred when the user passes the clipping times at the start and the end in addition to the input and output directories as arguments. It clips the audio at the start and at the end by the start and end durations specified by the user.
- This is the default made when the user only passes the input and output directories as arguments. It first segments the audio based on energy thresholding. It then removes the first and the last segments. The threshold is chosen carefully so that it is able to identify the segments of music as accurately as possible.

### Task 3

This Python script extracts text from PDF files, converts numbers to their word equivalents, removes punctuation, and converts the text to lowercase. When converting numbers to their word equivelents, it also identifies and handles ordinal numbers like '3rd'. It processes multiple PDFs from an input directory and saves the cleaned text as .txt files in a specified output directory. The script handles errors and ensures proper file management.

It was noticed that the heading in each transcript and references to slide time are not spoken out loud in the lectures. The headings are center aligned and bold, so the headings are removed from the transcript by removing all lines that are center aligned and bold. (Note that the number of heading lines in each transcript is different and cannot be removed by simply deleting a predefined number of lines) The references to slide title appear in individual lines in paranthesis and follow a similar text pattern. They are removed by finding the references using regular expressions and deleting thus identified lines.

It was also noticed that some symbols like the multiplication sign, addition symbol, and greek letters like alpha and theta couldn't be parsed appropriately. In fact, their encoding was corrupted and therefore, this case was difficult to handle.

### Task 4

This Python script generates a training manifest file in JSONL format by matching audio files with their corresponding text transcriptions based on lecture numbers. It checks that the lecture numbers in the audio and text files match, reads audio durations, and writes the manifest with relevant details, ensuring proper error handling for missing or incorrectly formatted files.

### Task 5

The t5_json.py script creates a copy of the JSON manifest file by updated with additional metrics needed for visualisation, including word count, character count, and segment duration, derived from audio files. I have also performed audio segmentation using decibel levels so that audio files are broken down into each spoken word. Metrics related to these segments such as number of segments per audio file and average duration of each segment, are also updated. The script processes the audio files, extracts segment information using librosa, and then calculates aggregates like total duration, vocabulary size, and segment statistics. The aggregates are stored to the updated JSON file as well.

The t5_dashboard.py script visualizes this updated data using Python Dash by loading the new JSONL file, converting it to a DataFrame, and generating multiple plots for audio file durations, word counts, segment details, and more. The visualizations provide insights into the audio data distributions and aggregate statistics. The dashboard is hosted locally.