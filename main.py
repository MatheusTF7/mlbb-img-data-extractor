#!/usr/bin/env python3
"""
Command-line interface for the MLBB Image Data Extractor.
"""

import argparse
import sys
from pathlib import Path

from mlbb_extractor import Pipeline


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Extract structured data from Mobile Legends end-game screenshots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-i", "--image",
        help="Path to a single screenshot image",
    )
    input_group.add_argument(
        "-m", "--multiple",
        nargs="+",
        help="Paths to multiple screenshot images",
    )
    input_group.add_argument(
        "-d", "--directory",
        help="Path to directory containing screenshot images",
    )
    
    # Output options
    parser.add_argument(
        "-o", "--output",
        default="output",
        help="Output directory (default: output)",
    )
    parser.add_argument(
        "-f", "--formats",
        nargs="+",
        choices=["csv", "json", "excel"],
        default=["csv", "json"],
        help="Export formats (default: csv json)",
    )
    parser.add_argument(
        "-n", "--name",
        default="game_stats",
        help="Base filename for output files (default: game_stats)",
    )
    
    # Processing options
    parser.add_argument(
        "--resize-scale",
        type=float,
        default=2.0,
        help="Image resize scale factor (default: 2.0)",
    )
    parser.add_argument(
        "--no-denoise",
        action="store_true",
        help="Skip image denoising",
    )
    parser.add_argument(
        "--threshold",
        choices=["binary", "adaptive", "otsu"],
        default="adaptive",
        help="Thresholding type (default: adaptive)",
    )
    parser.add_argument(
        "--tesseract-cmd",
        help="Path to tesseract executable (if not in PATH)",
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize pipeline
    print("Initializing MLBB Image Data Extractor...")
    pipeline = Pipeline(
        output_dir=args.output,
        tesseract_cmd=args.tesseract_cmd,
    )
    
    # Determine input type
    try:
        if args.image:
            print(f"Processing single image: {args.image}")
            result = pipeline.run(
                image_path=args.image,
                export_formats=args.formats,
                output_filename=args.name,
                resize_scale=args.resize_scale,
                apply_denoise=not args.no_denoise,
                threshold_type=args.threshold,
            )
        elif args.multiple:
            print(f"Processing {len(args.multiple)} images...")
            result = pipeline.run(
                image_paths=args.multiple,
                export_formats=args.formats,
                output_filename=args.name,
                resize_scale=args.resize_scale,
                apply_denoise=not args.no_denoise,
                threshold_type=args.threshold,
            )
        elif args.directory:
            print(f"Processing images from directory: {args.directory}")
            result = pipeline.run(
                directory_path=args.directory,
                export_formats=args.formats,
                output_filename=args.name,
                resize_scale=args.resize_scale,
                apply_denoise=not args.no_denoise,
                threshold_type=args.threshold,
            )
        
        # Display results
        print("\n" + "=" * 50)
        print("Processing Complete!")
        print("=" * 50)
        print(f"Total images processed: {result['total_processed']}")
        print("\nExported files:")
        for format_type, path in result['export_paths'].items():
            print(f"  {format_type.upper()}: {path}")
        
        print("\nExtracted data preview:")
        print(result['data'].head())
        
        return 0
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
