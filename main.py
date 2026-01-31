#!/usr/bin/env python3
"""
Command-line interface for the MLBB Image Data Extractor.
"""

import argparse
import sys
import json
from pathlib import Path

from mlbb_extractor import Pipeline, MLBBExtractor


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Extract structured data from Mobile Legends end-game screenshots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract data for a specific player
  python main.py -i screenshot.png -p MTF7

  # Extract all players from an image
  python main.py -i screenshot.png --all-players

  # Process multiple images (legacy mode)
  python main.py -m img1.png img2.png -f csv json

  # Process a directory (legacy mode)
  python main.py -d ./screenshots/ -o ./results/
        """
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
    
    # Player extraction options
    parser.add_argument(
        "-p", "--player",
        help="Nickname of the player to extract data for",
    )
    parser.add_argument(
        "--all-players",
        action="store_true",
        help="Extract data for all 5 players on my team",
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
        default=["json"],
        help="Export formats (default: json)",
    )
    parser.add_argument(
        "-n", "--name",
        default="player_stats",
        help="Base filename for output files (default: player_stats)",
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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output",
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize pipeline
    print("Initializing MLBB Image Data Extractor...")
    pipeline = Pipeline(
        output_dir=args.output,
        tesseract_cmd=args.tesseract_cmd,
    )
    
    try:
        # Player-specific extraction mode
        if args.image and (args.player or args.all_players):
            return process_player_extraction(args, pipeline)
        
        # Legacy mode - general processing
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
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


def process_player_extraction(args, pipeline: Pipeline) -> int:
    """
    Process player-specific extraction.
    
    Args:
        args: Parsed command line arguments
        pipeline: Pipeline instance
        
    Returns:
        Exit code
    """
    extractor = MLBBExtractor(tesseract_cmd=args.tesseract_cmd)
    
    print(f"Processing image: {args.image}")
    
    if args.all_players:
        # Extract all players
        print("Extracting data for all players on my team...")
        results = extractor.extract_all_players(args.image)
        
        if not results:
            print("No player data could be extracted.")
            return 1
        
        # Display results
        print("\n" + "=" * 50)
        print("Extraction Complete!")
        print("=" * 50)
        
        for player_data in results:
            print(f"\nPlayer {player_data['position']}: {player_data['nickname']}")
            print(f"  K/D/A: {player_data['kills']}/{player_data['deaths']}/{player_data['assists']}")
            print(f"  Gold: {player_data['gold']}")
            print(f"  Rating: {player_data['ratio']}")
            print(f"  Medal: {player_data['medal']}")
        
        # First player's match info
        if results:
            print(f"\nMatch Info:")
            print(f"  Result: {results[0]['result']}")
            print(f"  Score: {results[0]['my_team_score']} - {results[0]['adversary_team_score']}")
            print(f"  Duration: {results[0]['duration']}")
        
        # Export
        if "json" in args.formats:
            output_path = Path(args.output) / f"{args.name}.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\nExported to: {output_path}")
        
        return 0
    
    elif args.player:
        # Extract specific player
        print(f"Searching for player: {args.player}")
        
        game_data = extractor.extract_game_data(args.image, args.player)
        
        if game_data is None:
            print(f"\nPlayer '{args.player}' not found in the screenshot.")
            print("Make sure the nickname matches (partial matches are supported).")
            return 1
        
        # Display results
        print("\n" + "=" * 50)
        print("Extraction Complete!")
        print("=" * 50)
        
        result_dict = game_data.to_dict()
        
        print(f"\nPlayer: {result_dict['nickname']}")
        print(f"  Kills: {result_dict['kills']}")
        print(f"  Deaths: {result_dict['deaths']}")
        print(f"  Assists: {result_dict['assists']}")
        print(f"  Gold: {result_dict['gold']}")
        print(f"  Rating: {result_dict['ratio']}")
        print(f"  Medal: {result_dict['medal']}")
        print(f"\nMatch Info:")
        print(f"  Result: {result_dict['result']}")
        print(f"  Score: {result_dict['my_team_score']} - {result_dict['adversary_team_score']}")
        print(f"  Duration: {result_dict['duration']}")
        
        # Export
        if "json" in args.formats:
            output_path = Path(args.output) / f"{args.name}.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            print(f"\nExported to: {output_path}")
        
        return 0
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
