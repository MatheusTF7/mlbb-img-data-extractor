"""Image preprocessing module using OpenCV."""

import cv2
import numpy as np
from typing import Tuple, Optional


class ImagePreprocessor:
    """
    Handles image preprocessing for OCR optimization.
    Uses OpenCV to enhance image quality and prepare it for text extraction.
    """

    def __init__(self):
        """Initialize the ImagePreprocessor."""
        pass

    def load_image(self, image_path: str) -> np.ndarray:
        """
        Load an image from the specified path.

        Args:
            image_path: Path to the image file

        Returns:
            Loaded image as numpy array

        Raises:
            FileNotFoundError: If image file doesn't exist
        """
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Could not load image from {image_path}")
        return image

    def convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale.

        Args:
            image: Input image

        Returns:
            Grayscale image
        """
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image

    def apply_threshold(
        self, image: np.ndarray, threshold_type: str = "adaptive"
    ) -> np.ndarray:
        """
        Apply thresholding to enhance text regions.

        Args:
            image: Input grayscale image
            threshold_type: Type of thresholding ('binary', 'adaptive', 'otsu')

        Returns:
            Thresholded image
        """
        if threshold_type == "binary":
            _, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
            return thresh
        elif threshold_type == "otsu":
            _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return thresh
        else:  # adaptive
            return cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )

    def denoise(self, image: np.ndarray) -> np.ndarray:
        """
        Apply denoising to the image.

        Args:
            image: Input image

        Returns:
            Denoised image
        """
        return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)

    def resize_image(
        self, image: np.ndarray, scale_factor: float = 2.0
    ) -> np.ndarray:
        """
        Resize image to improve OCR accuracy.

        Args:
            image: Input image
            scale_factor: Scale factor for resizing

        Returns:
            Resized image
        """
        width = int(image.shape[1] * scale_factor)
        height = int(image.shape[0] * scale_factor)
        return cv2.resize(image, (width, height), interpolation=cv2.INTER_CUBIC)

    def detect_regions(
        self, image: np.ndarray
    ) -> list:
        """
        Detect relevant regions in the image (e.g., player stats areas).

        Args:
            image: Input image

        Returns:
            List of detected regions as (x, y, w, h) tuples
        """
        # Convert to grayscale if needed
        gray = self.convert_to_grayscale(image)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter and return bounding boxes of significant contours
        regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Filter small regions
            if w > 50 and h > 20:
                regions.append((x, y, w, h))
        
        return regions

    def extract_region(
        self, image: np.ndarray, region: Tuple[int, int, int, int]
    ) -> np.ndarray:
        """
        Extract a specific region from the image.

        Args:
            image: Input image
            region: Region coordinates as (x, y, width, height)

        Returns:
            Extracted region
        """
        x, y, w, h = region
        return image[y : y + h, x : x + w]

    def preprocess(
        self,
        image_path: str,
        resize_scale: float = 2.0,
        apply_denoise: bool = True,
        threshold_type: str = "adaptive",
    ) -> np.ndarray:
        """
        Complete preprocessing pipeline for an image.

        Args:
            image_path: Path to the image file
            resize_scale: Scale factor for resizing
            apply_denoise: Whether to apply denoising
            threshold_type: Type of thresholding to apply

        Returns:
            Preprocessed image ready for OCR
        """
        # Load image
        image = self.load_image(image_path)
        
        # Convert to grayscale
        gray = self.convert_to_grayscale(image)
        
        # Resize for better OCR
        resized = self.resize_image(gray, resize_scale)
        
        # Apply denoising if requested
        if apply_denoise:
            resized = self.denoise(resized)
        
        # Apply thresholding
        processed = self.apply_threshold(resized, threshold_type)
        
        return processed
