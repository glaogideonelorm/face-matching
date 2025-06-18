#!/usr/bin/env python3
"""
Face Matching CLI Tool

Compares student photos from two folders (WEAC vs. UG) and scores each pair 1-10,
flagging low-confidence matches.

Usage:
    python match_faces.py --weac WEAC_FOLDER --ug UG_FOLDER --out REPORT_FILE.xlsx
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
# Import face_recognition only when needed to avoid initialization issues
# import face_recognition
import cv2
from tqdm import tqdm


class FaceMatcher:
    """Face matching pipeline for comparing student photos."""
    
    def __init__(self):
        self.supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        self._face_recognition = None
    
    @property
    def face_recognition(self):
        """Lazy import of face_recognition to avoid initialization issues."""
        if self._face_recognition is None:
            try:
                import face_recognition
                self._face_recognition = face_recognition
            except ImportError as e:
                print(f"ERROR: Could not import face_recognition: {e}")
                print("Please ensure face_recognition is properly installed.")
                sys.exit(8)
        return self._face_recognition
    
    def extract_key_from_filename(self, filepath: str) -> str:
        """Extract key from filename (case-insensitive, no extension)."""
        return Path(filepath).stem.lower()
    
    def scan_folder(self, folder_path: str) -> Dict[str, str]:
        """Build map of {key → filepath} for images in folder."""
        folder = Path(folder_path)
        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        key_to_filepath = {}
        
        for file_path in folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                key = self.extract_key_from_filename(str(file_path))
                if key in key_to_filepath:
                    print(f"Warning: Duplicate key '{key}' found in {folder_path}")
                key_to_filepath[key] = str(file_path)
        
        return key_to_filepath
    
    def detect_face_encodings(self, image_path: str, key: str, source: str) -> np.ndarray:
        """
        Detect face and return encodings.
        
        Args:
            image_path: Path to image file
            key: Student key for error reporting
            source: 'weac' or 'ug' for error reporting
            
        Returns:
            Face encoding as numpy array
            
        Raises:
            SystemExit: If no face or multiple faces detected
        """
        # Load image
        image = self.face_recognition.load_image_file(image_path)
        
        # Find face locations
        face_locations = self.face_recognition.face_locations(image)
        
        if len(face_locations) == 0:
            print(f"ERROR: no face detected in {source} for key {key}")
            sys.exit(1)
        elif len(face_locations) > 1:
            print(f"ERROR: multiple faces detected in {source} for key {key}")
            sys.exit(2)
        
        # Get face encodings
        face_encodings = self.face_recognition.face_encodings(image, face_locations)
        
        if len(face_encodings) == 0:
            print(f"ERROR: could not encode face in {source} for key {key}")
            sys.exit(1)
        
        return face_encodings[0]
    
    def compute_similarity(self, encoding1: np.ndarray, encoding2: np.ndarray) -> float:
        """Compute cosine similarity between two face encodings."""
        # face_recognition uses Euclidean distance, but we want cosine similarity
        # We can use 1 - cosine_distance for similarity
        from numpy.linalg import norm
        
        # Normalize vectors
        encoding1_norm = encoding1 / norm(encoding1)
        encoding2_norm = encoding2 / norm(encoding2)
        
        # Cosine similarity = dot product of normalized vectors
        similarity = np.dot(encoding1_norm, encoding2_norm)
        
        # Ensure similarity is between 0 and 1
        similarity = max(0.0, min(1.0, similarity))
        
        return float(similarity)
    
    def map_to_rating(self, similarity_score: float) -> int:
        """Map similarity score to rating 1-10."""
        return round(similarity_score * 9 + 1)
    
    def process_student_pair(self, key: str, weac_path: str, ug_path: str) -> Dict:
        """Process a single student pair and return matching results."""
        try:
            # Detect faces and get encodings
            weac_encoding = self.detect_face_encodings(weac_path, key, 'weac')
            ug_encoding = self.detect_face_encodings(ug_path, key, 'ug')
            
            # Compute similarity
            similarity_score = self.compute_similarity(weac_encoding, ug_encoding)
            
            # Map to rating
            rating = self.map_to_rating(similarity_score)
            
            # Flag low confidence (rating 9 and below are considered non-matches)
            flagged = rating <= 9
            
            return {
                'key': key,
                'weac_filepath': weac_path,
                'ug_filepath': ug_path,
                'similarity_score': similarity_score,
                'rating': rating,
                'flagged': flagged
            }
            
        except SystemExit:
            # Re-raise system exits (face detection errors)
            raise
        except Exception as e:
            print(f"Error processing student {key}: {str(e)}")
            sys.exit(3)
    
    def match_faces(self, weac_folder: str, ug_folder: str, output_file: str):
        """Main face matching pipeline."""
        print("Scanning folders...")
        
        # Build maps of {key → filepath}
        weac_map = self.scan_folder(weac_folder)
        ug_map = self.scan_folder(ug_folder)
        
        print(f"Found {len(weac_map)} WEAC images and {len(ug_map)} UG images")
        
        # Find intersection of keys
        common_keys = set(weac_map.keys()) & set(ug_map.keys())
        
        if not common_keys:
            print("ERROR: No common students found between folders")
            sys.exit(4)
        
        print(f"Found {len(common_keys)} common students")
        
        # Report unmatched students
        weac_only = set(weac_map.keys()) - common_keys
        ug_only = set(ug_map.keys()) - common_keys
        
        if weac_only:
            print(f"Students only in WEAC folder: {sorted(weac_only)}")
        if ug_only:
            print(f"Students only in UG folder: {sorted(ug_only)}")
        
        # Process each student pair
        results = []
        
        print("Processing student pairs...")
        for key in tqdm(sorted(common_keys), desc="Matching faces"):
            result = self.process_student_pair(key, weac_map[key], ug_map[key])
            results.append(result)
        
        # Create DataFrame and save to Excel
        df = pd.DataFrame(results)
        
        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to Excel
        df.to_excel(output_file, index=False)
        
        # Print summary
        total_matches = len(results)
        flagged_count = sum(1 for r in results if r['flagged'])
        avg_rating = np.mean([r['rating'] for r in results])
        
        print(f"\nResults saved to: {output_file}")
        print(f"Total matches: {total_matches}")
        print(f"Flagged (low confidence): {flagged_count}")
        print(f"Average rating: {avg_rating:.2f}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Compare student photos from two folders and generate similarity report"
    )
    parser.add_argument(
        '--weac', 
        required=True,
        help='Path to folder containing WEAC images'
    )
    parser.add_argument(
        '--ug', 
        required=True,
        help='Path to folder containing UG images'
    )
    parser.add_argument(
        '--out', 
        required=True,
        help='Path to output Excel (.xlsx) report'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.weac):
        print(f"ERROR: WEAC folder not found: {args.weac}")
        sys.exit(5)
    
    if not os.path.exists(args.ug):
        print(f"ERROR: UG folder not found: {args.ug}")
        sys.exit(6)
    
    if not args.out.lower().endswith('.xlsx'):
        print("ERROR: Output file must have .xlsx extension")
        sys.exit(7)
    
    # Run face matching
    matcher = FaceMatcher()
    matcher.match_faces(args.weac, args.ug, args.out)


if __name__ == '__main__':
    main() 