"""Text extraction module using Tesseract OCR."""

import pytesseract
import numpy as np
from typing import Dict, List, Optional, Any
import re


class TextExtractor:
    """
    Handles text extraction from preprocessed images using Tesseract OCR.
    """

    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize the TextExtractor.

        Args:
            tesseract_cmd: Optional path to tesseract executable.
                          If None, uses system default.
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text(
        self, image: np.ndarray, config: str = "--psm 6"
    ) -> str:
        """
        Extract text from an image using Tesseract OCR.

        Args:
            image: Preprocessed image
            config: Tesseract configuration string

        Returns:
            Extracted text as string
        """
        try:
            text = pytesseract.image_to_string(image, config=config)
            return text.strip()
        except Exception as e:
            print(f"Error during text extraction: {e}")
            return ""

    def extract_text_with_boxes(
        self, image: np.ndarray
    ) -> List[Dict[str, Any]]:
        """
        Extract text along with bounding box information.

        Args:
            image: Preprocessed image

        Returns:
            List of dictionaries containing text and coordinates
        """
        try:
            data = pytesseract.image_to_data(
                image, output_type=pytesseract.Output.DICT
            )
            
            results = []
            n_boxes = len(data["text"])
            
            for i in range(n_boxes):
                if int(data["conf"][i]) > 0:  # Filter low confidence
                    results.append(
                        {
                            "text": data["text"][i],
                            "left": data["left"][i],
                            "top": data["top"][i],
                            "width": data["width"][i],
                            "height": data["height"][i],
                            "confidence": data["conf"][i],
                        }
                    )
            
            return results
        except Exception as e:
            print(f"Error during text extraction with boxes: {e}")
            return []

    def extract_numbers(self, image: np.ndarray) -> List[str]:
        """
        Extract numeric values from image.

        Args:
            image: Preprocessed image

        Returns:
            List of extracted numbers
        """
        text = self.extract_text(image, config="--psm 6 digits")
        numbers = re.findall(r"\d+", text)
        return numbers

    def extract_region_text(
        self, image: np.ndarray, regions: List[tuple]
    ) -> Dict[int, str]:
        """
        Extract text from multiple regions in an image.

        Args:
            image: Full preprocessed image
            regions: List of regions as (x, y, w, h) tuples

        Returns:
            Dictionary mapping region index to extracted text
        """
        results = {}
        
        for idx, region in enumerate(regions):
            x, y, w, h = region
            roi = image[y : y + h, x : x + w]
            text = self.extract_text(roi)
            results[idx] = text
        
        return results

    def extract_player_stats(self, image: np.ndarray) -> Dict[str, str]:
        """
        Extract player statistics from end-game screenshot.
        This is a specialized method for MLBB screenshots.

        Args:
            image: Preprocessed end-game screenshot

        Returns:
            Dictionary with extracted player statistics
        """
        text = self.extract_text(image)
        
        stats = {
            "kills": "",
            "deaths": "",
            "assists": "",
            "gold": "",
            "damage": "",
        }
        
        # Pattern matching for common stats
        # K/D/A pattern (e.g., "10/2/15")
        kda_pattern = r"(\d+)[/\-](\d+)[/\-](\d+)"
        kda_match = re.search(kda_pattern, text)
        if kda_match:
            stats["kills"] = kda_match.group(1)
            stats["deaths"] = kda_match.group(2)
            stats["assists"] = kda_match.group(3)
        
        # Gold pattern
        gold_pattern = r"(\d+\.?\d*)[kK]?\s*(?:gold|Gold)"
        gold_match = re.search(gold_pattern, text)
        if gold_match:
            stats["gold"] = gold_match.group(1)
        
        # Damage pattern
        damage_pattern = r"(\d+\.?\d*)[kK]?\s*(?:damage|Damage)"
        damage_match = re.search(damage_pattern, text)
        if damage_match:
            stats["damage"] = damage_match.group(1)
        
        return stats
