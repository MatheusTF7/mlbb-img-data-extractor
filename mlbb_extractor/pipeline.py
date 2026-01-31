"""Main pipeline for orchestrating the data extraction process."""

from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd

from .preprocessor.image_processor import ImagePreprocessor
from .ocr.text_extractor import TextExtractor
from .parser.data_parser import DataParser
from .exporter.data_exporter import DataExporter


class Pipeline:
    """
    Main pipeline that orchestrates the complete data extraction process
    from image preprocessing to data export.
    """

    def __init__(
        self,
        output_dir: str = "output",
        tesseract_cmd: Optional[str] = None,
    ):
        """
        Initialize the Pipeline with all components.

        Args:
            output_dir: Directory for output files
            tesseract_cmd: Optional path to tesseract executable
        """
        self.preprocessor = ImagePreprocessor()
        self.text_extractor = TextExtractor(tesseract_cmd=tesseract_cmd)
        self.data_parser = DataParser()
        self.data_exporter = DataExporter(output_dir=output_dir)

    def process_single_image(
        self,
        image_path: str,
        resize_scale: float = 2.0,
        apply_denoise: bool = True,
        threshold_type: str = "adaptive",
    ) -> Dict[str, Any]:
        """
        Process a single image through the complete pipeline.

        Args:
            image_path: Path to the image file
            resize_scale: Scale factor for resizing during preprocessing
            apply_denoise: Whether to apply denoising
            threshold_type: Type of thresholding to apply

        Returns:
            Dictionary with extracted and structured data
        """
        # Step 1: Preprocess the image
        processed_image = self.preprocessor.preprocess(
            image_path=image_path,
            resize_scale=resize_scale,
            apply_denoise=apply_denoise,
            threshold_type=threshold_type,
        )

        # Step 2: Extract text using OCR
        raw_text = self.text_extractor.extract_text(processed_image)
        
        # Step 3: Extract player stats
        player_stats = self.text_extractor.extract_player_stats(processed_image)

        # Step 4: Parse and structure the data
        structured_data = self.data_parser.structure_player_data(player_stats)
        
        # Add source image path
        structured_data["source_image"] = str(Path(image_path).name)
        structured_data["raw_text"] = raw_text

        return structured_data

    def process_multiple_images(
        self,
        image_paths: List[str],
        resize_scale: float = 2.0,
        apply_denoise: bool = True,
        threshold_type: str = "adaptive",
    ) -> List[Dict[str, Any]]:
        """
        Process multiple images through the pipeline.

        Args:
            image_paths: List of paths to image files
            resize_scale: Scale factor for resizing during preprocessing
            apply_denoise: Whether to apply denoising
            threshold_type: Type of thresholding to apply

        Returns:
            List of dictionaries with extracted and structured data
        """
        results = []
        
        for image_path in image_paths:
            try:
                result = self.process_single_image(
                    image_path=image_path,
                    resize_scale=resize_scale,
                    apply_denoise=apply_denoise,
                    threshold_type=threshold_type,
                )
                results.append(result)
                print(f"Successfully processed: {image_path}")
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                # Add error entry
                results.append({
                    "source_image": str(Path(image_path).name),
                    "error": str(e),
                })
        
        return results

    def process_directory(
        self,
        directory_path: str,
        pattern: str = "*.png",
        resize_scale: float = 2.0,
        apply_denoise: bool = True,
        threshold_type: str = "adaptive",
    ) -> List[Dict[str, Any]]:
        """
        Process all images in a directory.

        Args:
            directory_path: Path to directory containing images
            pattern: Glob pattern for image files
            resize_scale: Scale factor for resizing during preprocessing
            apply_denoise: Whether to apply denoising
            threshold_type: Type of thresholding to apply

        Returns:
            List of dictionaries with extracted and structured data
        """
        directory = Path(directory_path)
        image_paths = list(directory.glob(pattern))
        
        # Also try other common image extensions
        for ext in ["*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG"]:
            image_paths.extend(directory.glob(ext))
        
        image_paths = [str(p) for p in image_paths]
        
        print(f"Found {len(image_paths)} images in {directory_path}")
        
        return self.process_multiple_images(
            image_paths=image_paths,
            resize_scale=resize_scale,
            apply_denoise=apply_denoise,
            threshold_type=threshold_type,
        )

    def extract_player_data(
        self,
        image_path: str,
        player_nickname: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Extract data for a specific player from an MLBB screenshot.

        Args:
            image_path: Path to the screenshot image
            player_nickname: Nickname of the player to find

        Returns:
            Dictionary with player data or None if not found
        """
        from .extractor.mlbb_extractor import MLBBExtractor
        
        extractor = MLBBExtractor(tesseract_cmd=self.text_extractor.tesseract_cmd 
                                   if hasattr(self.text_extractor, 'tesseract_cmd') else None)
        
        game_data = extractor.extract_game_data(image_path, player_nickname)
        
        if game_data:
            return game_data.to_dict()
        return None

    def extract_all_players_data(
        self,
        image_path: str,
    ) -> List[Dict[str, Any]]:
        """
        Extract data for all players on my team from an MLBB screenshot.

        Args:
            image_path: Path to the screenshot image

        Returns:
            List of dictionaries with all players' data
        """
        from .extractor.mlbb_extractor import MLBBExtractor
        
        extractor = MLBBExtractor(tesseract_cmd=self.text_extractor.tesseract_cmd 
                                   if hasattr(self.text_extractor, 'tesseract_cmd') else None)
        
        return extractor.extract_all_players(image_path)

    def run(
        self,
        image_path: Optional[str] = None,
        image_paths: Optional[List[str]] = None,
        directory_path: Optional[str] = None,
        export_formats: Optional[List[str]] = None,
        output_filename: str = "game_stats",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Run the complete pipeline with automatic export.

        Args:
            image_path: Path to a single image (optional)
            image_paths: List of image paths (optional)
            directory_path: Path to directory with images (optional)
            export_formats: List of export formats ('csv', 'json', 'excel')
            output_filename: Base filename for output files
            **kwargs: Additional arguments passed to processing methods

        Returns:
            Dictionary with results and export paths
        """
        if export_formats is None:
            export_formats = ["csv", "json"]

        # Determine which processing method to use
        if image_path:
            results = [self.process_single_image(image_path, **kwargs)]
        elif image_paths:
            results = self.process_multiple_images(image_paths, **kwargs)
        elif directory_path:
            results = self.process_directory(directory_path, **kwargs)
        else:
            raise ValueError(
                "Must provide image_path, image_paths, or directory_path"
            )

        # Create DataFrame
        df = self.data_parser.create_dataframe(results)
        
        # Export data
        export_paths = self.data_exporter.export_multiple_formats(
            data=df,
            base_filename=output_filename,
            formats=export_formats,
        )

        return {
            "data": df,
            "export_paths": export_paths,
            "total_processed": len(results),
        }

    def run_player_extraction(
        self,
        image_path: str,
        player_nickname: str,
        export_formats: Optional[List[str]] = None,
        output_filename: str = "player_stats",
    ) -> Dict[str, Any]:
        """
        Run player-specific extraction pipeline.

        Args:
            image_path: Path to the screenshot image
            player_nickname: Nickname of the player to find
            export_formats: List of export formats
            output_filename: Base filename for output files

        Returns:
            Dictionary with player data and export paths
        """
        if export_formats is None:
            export_formats = ["json"]

        player_data = self.extract_player_data(image_path, player_nickname)
        
        if player_data is None:
            return {
                "data": None,
                "error": f"Player '{player_nickname}' not found",
                "export_paths": {},
            }

        # Export data
        export_paths = {}
        
        if "json" in export_formats:
            json_path = self.data_exporter.export_to_json(
                player_data, f"{output_filename}.json"
            )
            export_paths["json"] = json_path
        
        if "csv" in export_formats:
            import pandas as pd
            df = pd.DataFrame([player_data])
            csv_path = self.data_exporter.export_to_csv(
                df, f"{output_filename}.csv"
            )
            export_paths["csv"] = csv_path

        return {
            "data": player_data,
            "export_paths": export_paths,
        }

