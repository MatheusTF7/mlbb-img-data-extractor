#!/usr/bin/env python3
"""
Test script to verify the MLBB extractor functionality with synthetic data.
"""

import numpy as np
import cv2
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mlbb_extractor import (
    ImagePreprocessor,
    TextExtractor,
    DataParser,
    DataExporter,
    Pipeline
)


def create_test_image():
    """Create a simple test image with text."""
    # Create a white background
    img = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Add some text to simulate game stats
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "Player: TestPlayer", (50, 100), font, 1, (0, 0, 0), 2)
    cv2.putText(img, "Hero: Layla", (50, 150), font, 1, (0, 0, 0), 2)
    cv2.putText(img, "K/D/A: 10/2/15", (50, 200), font, 1, (0, 0, 0), 2)
    cv2.putText(img, "Gold: 16.5k", (50, 250), font, 1, (0, 0, 0), 2)
    cv2.putText(img, "Damage: 89.2k", (50, 300), font, 1, (0, 0, 0), 2)
    cv2.putText(img, "Result: Victory", (50, 350), font, 1, (0, 0, 0), 2)
    cv2.putText(img, "Duration: 18:45", (50, 400), font, 1, (0, 0, 0), 2)
    
    return img


def test_preprocessing():
    """Test image preprocessing."""
    print("\n" + "=" * 50)
    print("Testing Image Preprocessing")
    print("=" * 50)
    
    # Create test image
    test_img = create_test_image()
    test_path = "/tmp/test_screenshot.png"
    cv2.imwrite(test_path, test_img)
    print(f"✓ Created test image at {test_path}")
    
    # Test preprocessor
    preprocessor = ImagePreprocessor()
    
    # Load image
    img = preprocessor.load_image(test_path)
    print(f"✓ Loaded image with shape: {img.shape}")
    
    # Convert to grayscale
    gray = preprocessor.convert_to_grayscale(img)
    print(f"✓ Converted to grayscale: {gray.shape}")
    
    # Resize
    resized = preprocessor.resize_image(gray, scale_factor=2.0)
    print(f"✓ Resized image: {resized.shape}")
    
    # Apply threshold
    thresh = preprocessor.apply_threshold(resized, threshold_type="adaptive")
    print(f"✓ Applied thresholding: {thresh.shape}")
    
    # Full preprocessing
    processed = preprocessor.preprocess(test_path)
    print(f"✓ Full preprocessing completed: {processed.shape}")
    
    return test_path


def test_ocr(test_path):
    """Test OCR text extraction."""
    print("\n" + "=" * 50)
    print("Testing OCR Text Extraction")
    print("=" * 50)
    
    preprocessor = ImagePreprocessor()
    text_extractor = TextExtractor()
    
    # Preprocess image
    processed = preprocessor.preprocess(test_path, threshold_type="binary")
    
    # Extract text
    text = text_extractor.extract_text(processed)
    print(f"✓ Extracted text (length: {len(text)} chars)")
    print(f"  Preview: {text[:100]}...")
    
    # Extract with boxes
    boxes = text_extractor.extract_text_with_boxes(processed)
    print(f"✓ Extracted {len(boxes)} text regions with bounding boxes")
    
    return processed


def test_parsing():
    """Test data parsing."""
    print("\n" + "=" * 50)
    print("Testing Data Parsing")
    print("=" * 50)
    
    parser = DataParser()
    
    # Test K/D/A parsing
    kda = parser.parse_kda("10/2/15")
    print(f"✓ Parsed K/D/A: {kda}")
    assert kda["kills"] == 10
    assert kda["deaths"] == 2
    assert kda["assists"] == 15
    
    # Test gold parsing
    gold = parser.parse_gold("16.5k")
    print(f"✓ Parsed gold: {gold}")
    assert gold == 16500.0
    
    # Test damage parsing
    damage = parser.parse_damage("89.2k")
    print(f"✓ Parsed damage: {damage}")
    assert damage == 89200.0
    
    # Test game result
    result = parser.parse_game_result("Victory")
    print(f"✓ Parsed game result: {result}")
    assert result == "Victory"
    
    # Test duration
    duration = parser.parse_game_duration("18:45")
    print(f"✓ Parsed duration: {duration} seconds")
    assert duration == 1125
    
    # Test structure
    data = {
        "player_name": "TestPlayer",
        "hero_name": "Layla",
        "kda": "10/2/15",
        "gold": "16.5k",
        "damage": "89.2k",
        "game_result": "Victory",
        "duration": "18:45"
    }
    structured = parser.structure_player_data(data)
    print(f"✓ Structured data: {structured}")
    
    # Create DataFrame
    df = parser.create_dataframe([structured])
    print(f"✓ Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
    print(df)


def test_export():
    """Test data export."""
    print("\n" + "=" * 50)
    print("Testing Data Export")
    print("=" * 50)
    
    parser = DataParser()
    exporter = DataExporter(output_dir="/tmp/test_output")
    
    # Create sample data
    data = {
        "player_name": "TestPlayer",
        "hero_name": "Layla",
        "kda": "10/2/15",
        "gold": "16.5k",
        "damage": "89.2k",
        "game_result": "Victory",
        "duration": "18:45"
    }
    structured = parser.structure_player_data(data)
    df = parser.create_dataframe([structured])
    
    # Export to CSV
    csv_path = exporter.export_to_csv(df, "test_game.csv")
    print(f"✓ Exported to CSV: {csv_path}")
    assert Path(csv_path).exists()
    
    # Export to JSON
    json_path = exporter.export_to_json(df, "test_game.json")
    print(f"✓ Exported to JSON: {json_path}")
    assert Path(json_path).exists()
    
    # Export multiple formats
    export_paths = exporter.export_multiple_formats(df, "test_all")
    print(f"✓ Exported to multiple formats:")
    for fmt, path in export_paths.items():
        print(f"  - {fmt}: {path}")
        assert Path(path).exists()


def test_pipeline(test_path):
    """Test complete pipeline."""
    print("\n" + "=" * 50)
    print("Testing Complete Pipeline")
    print("=" * 50)
    
    pipeline = Pipeline(output_dir="/tmp/test_output")
    
    # Process single image
    result = pipeline.run(
        image_path=test_path,
        export_formats=["csv", "json"],
        output_filename="pipeline_test"
    )
    
    print(f"✓ Processed {result['total_processed']} image(s)")
    print(f"✓ Export paths:")
    for fmt, path in result['export_paths'].items():
        print(f"  - {fmt}: {path}")
    
    print(f"\n✓ Extracted data:")
    print(result['data'])


def main():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("MLBB Image Data Extractor - Functionality Tests")
    print("=" * 50)
    
    try:
        # Run tests
        test_path = test_preprocessing()
        test_ocr(test_path)
        test_parsing()
        test_export()
        test_pipeline(test_path)
        
        print("\n" + "=" * 50)
        print("✓ All tests passed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
