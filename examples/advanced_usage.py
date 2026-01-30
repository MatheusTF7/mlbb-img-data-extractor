"""Advanced example showing component-level usage."""

from mlbb_extractor import (
    ImagePreprocessor,
    TextExtractor,
    DataParser,
    DataExporter,
)


def main():
    """Demonstrate using individual components."""
    
    # Initialize components
    preprocessor = ImagePreprocessor()
    text_extractor = TextExtractor()
    data_parser = DataParser()
    data_exporter = DataExporter(output_dir="output")
    
    print("Advanced Example: Using individual components")
    print("=" * 50)
    
    image_path = "examples/sample_screenshot.png"
    
    try:
        # Step 1: Load and preprocess image
        print("\n1. Preprocessing image...")
        image = preprocessor.load_image(image_path)
        print(f"   Loaded image with shape: {image.shape}")
        
        # Apply custom preprocessing
        gray = preprocessor.convert_to_grayscale(image)
        resized = preprocessor.resize_image(gray, scale_factor=2.5)
        denoised = preprocessor.denoise(resized)
        processed = preprocessor.apply_threshold(denoised, threshold_type="otsu")
        print(f"   Preprocessed image ready for OCR")
        
        # Step 2: Extract text
        print("\n2. Extracting text...")
        raw_text = text_extractor.extract_text(processed)
        print(f"   Extracted text:\n   {raw_text[:100]}...")
        
        # Extract with bounding boxes
        text_boxes = text_extractor.extract_text_with_boxes(processed)
        print(f"   Found {len(text_boxes)} text regions")
        
        # Step 3: Detect and process regions
        print("\n3. Detecting regions...")
        regions = preprocessor.detect_regions(image)
        print(f"   Detected {len(regions)} regions")
        
        # Extract text from each region
        if regions:
            region_texts = text_extractor.extract_region_text(processed, regions[:3])
            print(f"   Extracted text from {len(region_texts)} regions")
        
        # Step 4: Parse data
        print("\n4. Parsing data...")
        
        # Example: Parse K/D/A
        test_kda = "Player stats: 15/3/20"
        kda = data_parser.parse_kda(test_kda)
        print(f"   K/D/A: {kda}")
        
        # Parse gold
        test_gold = "Total gold: 18.5k"
        gold = data_parser.parse_gold(test_gold)
        print(f"   Gold: {gold}")
        
        # Step 5: Structure data
        print("\n5. Structuring data...")
        mock_data = {
            "player_name": "TestPlayer",
            "hero_name": "Layla",
            "kda": "10/2/15",
            "gold": "16.3k",
            "damage": "89.2k",
            "game_result": "Victory",
            "duration": "18:45",
        }
        
        structured = data_parser.structure_player_data(mock_data)
        print(f"   Structured data: {structured}")
        
        # Step 6: Export data
        print("\n6. Exporting data...")
        df = data_parser.create_dataframe([structured])
        
        csv_path = data_exporter.export_to_csv(df, "advanced_example.csv")
        print(f"   CSV exported to: {csv_path}")
        
        json_path = data_exporter.export_to_json(df, "advanced_example.json")
        print(f"   JSON exported to: {json_path}")
        
        # Save raw text
        text_path = data_exporter.save_raw_text(raw_text, "raw_text.txt")
        print(f"   Raw text saved to: {text_path}")
        
        print("\n✓ Advanced example completed successfully!")
        
    except FileNotFoundError:
        print("\n✗ Sample image not found.")
        print("   Please place a screenshot at: examples/sample_screenshot.png")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()
