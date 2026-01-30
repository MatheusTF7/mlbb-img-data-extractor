# Example Usage Guide

This directory contains example scripts demonstrating how to use the MLBB Image Data Extractor.

## Files

- **basic_usage.py**: Basic examples showing how to use the Pipeline class
- **advanced_usage.py**: Advanced examples showing how to use individual components

## Running Examples

### Basic Usage

```bash
python examples/basic_usage.py
```

This will demonstrate:
- Processing a single image
- Processing multiple images
- Processing all images in a directory
- Custom preprocessing parameters

### Advanced Usage

```bash
python examples/advanced_usage.py
```

This will demonstrate:
- Using individual components (preprocessor, extractor, parser, exporter)
- Custom preprocessing workflows
- Manual control over each step

## Note

The examples expect sample images in the `examples/` directory. You can:
1. Add your own Mobile Legends screenshots
2. Modify the paths in the example scripts to point to your images

## Sample Image Requirements

For best results, use:
- High-quality screenshots (1080p or higher recommended)
- Clear text (not blurry)
- End-game statistics screen
- PNG or JPEG format
