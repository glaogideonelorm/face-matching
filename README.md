# Face Matching CLI Tool

A command-line tool that compares student photos from two folders  and scores each pair on a scale of 1-10, flagging low-confidence matches.

## Features

- **Automated Face Matching**: Uses `face_recognition` library with dlib for robust face detection and encoding


- **Excel Output**: Generates detailed reports in `.xlsx` format
- **Progress Tracking**: Shows progress bar during processing
- **Duplicate Detection**: Warns about duplicate keys in source folders

## Installation

### Prerequisites

- Python 3.8 or higher
- CMake (required for dlib compilation)
- Visual Studio Build Tools (Windows) or build-essential (Linux)


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


- Supports: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`

### 3. Face Detection & Encoding



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


## License

This tool is provided as-is for educational and research purposes.
