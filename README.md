# MLBB Image Data Extractor

A Python project to extract structured data from Mobile Legends Bang Bang (MLBB) end-game screenshots. This tool uses OpenCV for image preprocessing, Tesseract OCR for text extraction, and Pandas for data handling and export. The pipeline processes images, detects relevant regions, parses game statistics, and outputs the results in structured formats such as CSV or JSON.

## Features

- **Image Preprocessing**: Uses OpenCV to enhance image quality for optimal OCR results
  - Grayscale conversion
  - Image resizing for better OCR accuracy
  - Denoising
  - Adaptive/Otsu/Binary thresholding
  - Region detection

- **Text Extraction**: Leverages Tesseract OCR to extract text from screenshots
  - Raw text extraction
  - Text with bounding boxes
  - Region-specific text extraction
  - Player statistics extraction

- **Data Parsing**: Intelligent parsing of game statistics
  - K/D/A (Kills/Deaths/Assists) parsing
  - Gold and damage parsing (handles K notation)
  - Player and hero name extraction
  - Game result detection
  - Game duration parsing

- **Data Export**: Multiple export formats supported
  - CSV export
  - JSON export
  - Excel export (optional)
  - Append to existing files

## Installation

### Prerequisites

1. **Python 3.8 or higher**

2. **Tesseract OCR**: Install Tesseract on your system
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`
   - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### Command Line Interface

Process a single image:
```bash
python main.py -i path/to/screenshot.png
```

Process multiple images:
```bash
python main.py -m image1.png image2.png image3.png
```

Process all images in a directory:
```bash
python main.py -d path/to/screenshots/
```

### Python API

```python
from mlbb_extractor import Pipeline

# Initialize the pipeline
pipeline = Pipeline(output_dir="output")

# Process a single image
result = pipeline.run(
    image_path="screenshot.png",
    export_formats=["csv", "json"],
    output_filename="game_stats"
)

print(f"Processed {result['total_processed']} images")
print(f"Results saved to: {result['export_paths']}")
```

## Usage Examples

### Basic Usage

```python
from mlbb_extractor import Pipeline

# Create pipeline
pipeline = Pipeline(output_dir="results")

# Process single screenshot
result = pipeline.run(
    image_path="examples/game1.png",
    export_formats=["csv", "json"],
    output_filename="single_game"
)

# Access the DataFrame
df = result['data']
print(df)
```

### Advanced Usage - Using Individual Components

```python
from mlbb_extractor import (
    ImagePreprocessor,
    TextExtractor,
    DataParser,
    DataExporter
)

# Initialize components
preprocessor = ImagePreprocessor()
text_extractor = TextExtractor()
data_parser = DataParser()
data_exporter = DataExporter(output_dir="output")

# Process image step by step
image = preprocessor.load_image("screenshot.png")
processed = preprocessor.preprocess("screenshot.png")
text = text_extractor.extract_text(processed)
stats = text_extractor.extract_player_stats(processed)
structured_data = data_parser.structure_player_data(stats)

# Export
df = data_parser.create_dataframe([structured_data])
data_exporter.export_to_csv(df, "results.csv")
```

### Custom Preprocessing Parameters

```python
result = pipeline.run(
    image_path="screenshot.png",
    resize_scale=3.0,           # Larger resize for better OCR
    apply_denoise=False,        # Skip denoising
    threshold_type="otsu",      # Use Otsu thresholding
    export_formats=["csv", "json"]
)
```

## Command Line Options

```
usage: main.py [-h] (-i IMAGE | -m MULTIPLE [MULTIPLE ...] | -d DIRECTORY)
               [-o OUTPUT] [-f {csv,json,excel} [{csv,json,excel} ...]]
               [-n NAME] [--resize-scale RESIZE_SCALE] [--no-denoise]
               [--threshold {binary,adaptive,otsu}]
               [--tesseract-cmd TESSERACT_CMD]

Extract structured data from Mobile Legends end-game screenshots

optional arguments:
  -h, --help            show this help message and exit
  -i IMAGE, --image IMAGE
                        Path to a single screenshot image
  -m MULTIPLE [MULTIPLE ...], --multiple MULTIPLE [MULTIPLE ...]
                        Paths to multiple screenshot images
  -d DIRECTORY, --directory DIRECTORY
                        Path to directory containing screenshot images
  -o OUTPUT, --output OUTPUT
                        Output directory (default: output)
  -f {csv,json,excel} [{csv,json,excel} ...], --formats {csv,json,excel} [{csv,json,excel} ...]
                        Export formats (default: csv json)
  -n NAME, --name NAME  Base filename for output files (default: game_stats)
  --resize-scale RESIZE_SCALE
                        Image resize scale factor (default: 2.0)
  --no-denoise          Skip image denoising
  --threshold {binary,adaptive,otsu}
                        Thresholding type (default: adaptive)
  --tesseract-cmd TESSERACT_CMD
                        Path to tesseract executable (if not in PATH)
```

## Project Structure

```
mlbb-img-data-extractor/
├── mlbb_extractor/           # Main package
│   ├── __init__.py          # Package initialization
│   ├── pipeline.py          # Main pipeline orchestrator
│   ├── config.py            # Configuration management
│   ├── preprocessor/        # Image preprocessing module
│   │   ├── __init__.py
│   │   └── image_processor.py
│   ├── ocr/                 # OCR text extraction module
│   │   ├── __init__.py
│   │   └── text_extractor.py
│   ├── parser/              # Data parsing module
│   │   ├── __init__.py
│   │   └── data_parser.py
│   └── exporter/            # Data export module
│       ├── __init__.py
│       └── data_exporter.py
├── examples/                # Example scripts
│   ├── basic_usage.py
│   └── advanced_usage.py
├── tests/                   # Test suite
├── main.py                  # CLI entry point
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore file
├── LICENSE                 # MIT License
└── README.md               # This file
```

## Output Format

### CSV Output
```csv
player_name,hero_name,kills,deaths,assists,gold,damage,game_result,duration,source_image
Player1,Layla,10,2,15,16300.0,89200.0,Victory,1125,screenshot1.png
Player2,Tigreal,5,8,20,12500.0,45600.0,Defeat,945,screenshot2.png
```

### JSON Output
```json
[
  {
    "player_name": "Player1",
    "hero_name": "Layla",
    "kills": 10,
    "deaths": 2,
    "assists": 15,
    "gold": 16300.0,
    "damage": 89200.0,
    "game_result": "Victory",
    "duration": 1125,
    "source_image": "screenshot1.png"
  }
]
```

## Configuration

Create a `config.json` file to customize processing parameters:

```json
{
  "preprocessing": {
    "resize_scale": 2.5,
    "apply_denoise": true,
    "threshold_type": "otsu"
  },
  "ocr": {
    "tesseract_cmd": "/usr/bin/tesseract",
    "config": "--psm 6 --oem 3"
  },
  "export": {
    "output_dir": "results",
    "default_formats": ["csv", "json"],
    "default_filename": "mlbb_stats"
  }
}
```

## Requirements

- Python >= 3.8
- opencv-python >= 4.8.0
- pytesseract >= 0.3.10
- pandas >= 2.0.0
- numpy >= 1.24.0
- Pillow >= 10.0.0

## Troubleshooting

### Tesseract not found
If you get "Tesseract not found" error, install Tesseract OCR or specify the path:

```python
pipeline = Pipeline(tesseract_cmd="/path/to/tesseract")
```

Or via CLI:
```bash
python main.py -i image.png --tesseract-cmd /path/to/tesseract
```

### Poor OCR results
Try adjusting preprocessing parameters:
- Increase `resize_scale` (try 3.0 or higher)
- Try different `threshold_type` (adaptive, otsu, binary)
- Ensure screenshots are high quality

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenCV for image processing capabilities
- Tesseract OCR for text extraction
- Pandas for data manipulation

## Author

MatheusTF7

---

*Um projeto de teste para extrair dados de uma screenshot de final de partida do Mobile Legends.*
