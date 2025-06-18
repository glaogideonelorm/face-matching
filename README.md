# Face Matching CLI Tool

A command-line tool that compares student photos from two folders (WEAC vs. UG) and scores each pair on a scale of 1-10, flagging low-confidence matches.

## Features

- **Automated Face Matching**: Uses `face_recognition` library with dlib for robust face detection and encoding
- **Similarity Scoring**: Computes cosine similarity between face encodings and maps to 1-10 rating scale
- **Error Handling**: Exits gracefully with specific error codes for no face/multiple faces detection
- **Excel Output**: Generates detailed reports in `.xlsx` format
- **Progress Tracking**: Shows progress bar during processing
- **Duplicate Detection**: Warns about duplicate keys in source folders

## Installation

### Prerequisites

- Python 3.8 or higher
- CMake (required for dlib compilation)
- Visual Studio Build Tools (Windows) or build-essential (Linux)

### macOS Installation

```bash
# Install system dependencies
brew install cmake

# Clone/setup the project
cd face-matching

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Linux Installation

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install build-essential cmake python3-dev

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Windows Installation

```bash
# Install Visual Studio Build Tools first
# Then create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

**Note**: Always activate the virtual environment before using the tool:

```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

## Usage

### Basic Command

```bash
# Make sure virtual environment is activated first
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

python match_faces.py --weac /path/to/weac/folder --ug /path/to/ug/folder --out report.xlsx
```

### Arguments

- `--weac WEAC_FOLDER`: Path to folder containing WEAC student images
- `--ug UG_FOLDER`: Path to folder containing UG student images
- `--out REPORT_FILE.xlsx`: Path for output Excel report

### Example

```bash
python match_faces.py --weac ./data/weac_photos --ug ./data/ug_photos --out ./results/matching_report.xlsx
```

## How It Works

### 1. Key Extraction

- Extracts student keys from filenames (case-insensitive, no extension)
- Example: `john_doe.jpg` → key: `john_doe`

### 2. Folder Scanning

- Builds maps of `{key → filepath}` for both WEAC and UG folders
- Supports: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`

### 3. Face Detection & Encoding

- Detects faces in each image using `face_recognition`
- Generates 128-dimensional face embeddings with dlib
- **Exits with error if**:
  - No face detected (exit code 1)
  - Multiple faces detected (exit code 2)

### 4. Similarity Computation

- Computes cosine similarity between face encodings (0.0-1.0)
- Maps to rating: `rating = round(similarity_score * 9 + 1)`
- Flags matches with rating ≤ 9 as potential non-matches (only rating 10 = confirmed match)

### 5. Report Generation

- Creates Excel file with columns:
  - `key`: Student identifier
  - `weac_filepath`: Path to WEAC image
  - `ug_filepath`: Path to UG image
  - `similarity_score`: Raw similarity (0.0-1.0)
  - `rating`: Mapped rating (1-10)
  - `flagged`: Boolean for low confidence matches

## Output Example

| key        | weac_filepath        | ug_filepath        | similarity_score | rating | flagged |
| ---------- | -------------------- | ------------------ | ---------------- | ------ | ------- |
| john_doe   | /weac/john_doe.jpg   | /ug/john_doe.png   | 0.87             | 9      | False   |
| jane_smith | /weac/jane_smith.jpg | /ug/jane_smith.jpg | 0.34             | 4      | True    |

## Error Codes

- `1`: No face detected in image
- `2`: Multiple faces detected in image
- `3`: General processing error
- `4`: No common students found between folders
- `5`: WEAC folder not found
- `6`: UG folder not found
- `7`: Invalid output file extension
- `8`: Face recognition library import error

## Performance Notes

- Processing time depends on image count and resolution
- Typical processing: ~1-3 seconds per student pair
- Progress bar shows current status
- Consider batch processing for large datasets

## Troubleshooting

### Installation Issues

1. **dlib compilation fails**: Install CMake and build tools

   ```bash
   # macOS
   brew install cmake

   # Linux
   sudo apt-get install build-essential cmake python3-dev
   ```

2. **face_recognition install fails**: Update pip and try `pip install --upgrade face_recognition`

3. **"externally-managed-environment" error**: Create and use a virtual environment (required for modern Python)

4. **Memory errors**: Process smaller batches or increase system RAM

### Runtime Issues

1. **"No face detected"**: Check image quality and face visibility
2. **"Multiple faces detected"**: Crop images to single person
3. **Low similarity scores**: Verify images are of the same person
4. **Virtual environment not activated**: Run `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)

## License

This tool is provided as-is for educational and research purposes.
