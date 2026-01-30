"""Example script demonstrating how to use the MLBB Image Data Extractor."""

from mlbb_extractor import Pipeline


def main():
    """Main example function."""
    
    # Initialize the pipeline
    pipeline = Pipeline(output_dir="output")
    
    # Example 1: Process a single image
    print("Example 1: Processing a single image")
    print("-" * 50)
    try:
        result = pipeline.run(
            image_path="examples/sample_screenshot.png",
            export_formats=["csv", "json"],
            output_filename="single_game",
        )
        print(f"Processed {result['total_processed']} image(s)")
        print(f"Exports saved to: {result['export_paths']}")
        print("\nExtracted data:")
        print(result['data'])
    except FileNotFoundError:
        print("Sample image not found. Please provide a valid image path.")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n")
    
    # Example 2: Process multiple images
    print("Example 2: Processing multiple images")
    print("-" * 50)
    try:
        result = pipeline.run(
            image_paths=[
                "examples/game1.png",
                "examples/game2.png",
                "examples/game3.png",
            ],
            export_formats=["csv", "json"],
            output_filename="multiple_games",
        )
        print(f"Processed {result['total_processed']} image(s)")
        print(f"Exports saved to: {result['export_paths']}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n")
    
    # Example 3: Process all images in a directory
    print("Example 3: Processing images from a directory")
    print("-" * 50)
    try:
        result = pipeline.run(
            directory_path="examples/screenshots",
            export_formats=["csv", "json"],
            output_filename="all_games",
        )
        print(f"Processed {result['total_processed']} image(s)")
        print(f"Exports saved to: {result['export_paths']}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n")
    
    # Example 4: Custom preprocessing parameters
    print("Example 4: Custom preprocessing parameters")
    print("-" * 50)
    try:
        result = pipeline.run(
            image_path="examples/sample_screenshot.png",
            resize_scale=3.0,  # Larger resize for better OCR
            apply_denoise=False,  # Skip denoising
            threshold_type="otsu",  # Use Otsu thresholding
            export_formats=["csv"],
            output_filename="custom_processing",
        )
        print(f"Processed with custom parameters")
        print(f"Exports saved to: {result['export_paths']}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
