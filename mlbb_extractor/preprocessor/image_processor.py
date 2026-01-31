"""Image preprocessing module using OpenCV."""

import cv2
import numpy as np
from typing import Tuple, Optional, List
from enum import Enum


class PreprocessingMethod(Enum):
    """Available preprocessing methods for OCR optimization."""
    GRAYSCALE = "grayscale"
    GRAYSCALE_SCALED = "grayscale_scaled"
    THRESHOLD = "threshold"
    HIGH_CONTRAST = "high_contrast"
    INVERTED = "inverted"
    YELLOW_COLOR_MASK = "yellow_color_mask"
    WHITE_COLOR_MASK = "white_color_mask"


class ImagePreprocessor:
    """
    Handles image preprocessing for OCR optimization.
    Uses OpenCV to enhance image quality and prepare it for text extraction.
    """

    # Default HSV ranges for color masks
    YELLOW_HSV_LOWER = np.array([15, 40, 120])
    YELLOW_HSV_UPPER = np.array([45, 255, 255])
    
    WHITE_HSV_LOWER = np.array([0, 0, 180])
    WHITE_HSV_UPPER = np.array([180, 50, 255])

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
            scale_factor: Scale factor for resizing (must be positive)

        Returns:
            Resized image
            
        Raises:
            ValueError: If scale_factor is not positive
        """
        if scale_factor <= 0:
            raise ValueError("scale_factor must be positive")
        
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

    # =========================================================================
    # MLBB-Specific Preprocessing Methods
    # Based on PREPROCESSING_GUIDE.md recommendations
    # =========================================================================

    def preprocess_grayscale_scaled(
        self, 
        region: np.ndarray, 
        scale_factor: float = 2.0
    ) -> np.ndarray:
        """
        Grayscale with scaling - good for most text/numbers with good contrast.
        
        Args:
            region: Input image region (BGR or grayscale)
            scale_factor: Scale factor for upscaling
            
        Returns:
            Preprocessed grayscale scaled image
        """
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            gray = region
        scaled = cv2.resize(gray, None, fx=scale_factor, fy=scale_factor, 
                           interpolation=cv2.INTER_CUBIC)
        return scaled

    def preprocess_threshold(
        self, 
        region: np.ndarray, 
        scale_factor: float = 4.0,
        threshold_value: int = 127
    ) -> np.ndarray:
        """
        Binary threshold - good for high contrast text on uniform background.
        
        Args:
            region: Input image region
            scale_factor: Scale factor for upscaling
            threshold_value: Threshold value for binary conversion
            
        Returns:
            Thresholded binary image
        """
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            gray = region
        _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
        scaled = cv2.resize(binary, None, fx=scale_factor, fy=scale_factor,
                           interpolation=cv2.INTER_CUBIC)
        return scaled

    def preprocess_high_contrast(
        self, 
        region: np.ndarray, 
        scale_factor: float = 4.0
    ) -> np.ndarray:
        """
        Adaptive threshold - good for uneven lighting or shadows.
        
        Args:
            region: Input image region
            scale_factor: Scale factor for upscaling
            
        Returns:
            Adaptive thresholded image
        """
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            gray = region
        adaptive = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        scaled = cv2.resize(adaptive, None, fx=scale_factor, fy=scale_factor,
                           interpolation=cv2.INTER_CUBIC)
        return scaled

    def preprocess_inverted(
        self, 
        region: np.ndarray, 
        scale_factor: float = 4.0
    ) -> np.ndarray:
        """
        Inverted colors - good for light text on dark background.
        
        Args:
            region: Input image region
            scale_factor: Scale factor for upscaling
            
        Returns:
            Inverted and scaled image
        """
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            gray = region
        inverted = 255 - gray
        scaled = cv2.resize(inverted, None, fx=scale_factor, fy=scale_factor,
                           interpolation=cv2.INTER_CUBIC)
        return scaled

    def preprocess_yellow_color_mask(
        self, 
        region: np.ndarray, 
        scale_factor: float = 5.0,
        lower_hsv: Optional[np.ndarray] = None,
        upper_hsv: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Yellow/gold color mask - good for gold badges and yellow numbers.
        
        Args:
            region: Input image region (must be BGR)
            scale_factor: Scale factor for upscaling
            lower_hsv: Lower HSV bound (default: [15, 40, 120])
            upper_hsv: Upper HSV bound (default: [45, 255, 255])
            
        Returns:
            Color masked and scaled image
        """
        if lower_hsv is None:
            lower_hsv = self.YELLOW_HSV_LOWER
        if upper_hsv is None:
            upper_hsv = self.YELLOW_HSV_UPPER
            
        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
        scaled = cv2.resize(mask, None, fx=scale_factor, fy=scale_factor,
                           interpolation=cv2.INTER_CUBIC)
        return scaled

    def preprocess_white_color_mask(
        self, 
        region: np.ndarray, 
        scale_factor: float = 4.0,
        lower_hsv: Optional[np.ndarray] = None,
        upper_hsv: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        White color mask - good for white text on colored backgrounds.
        
        Args:
            region: Input image region (must be BGR)
            scale_factor: Scale factor for upscaling
            lower_hsv: Lower HSV bound
            upper_hsv: Upper HSV bound
            
        Returns:
            Color masked and scaled image
        """
        if lower_hsv is None:
            lower_hsv = self.WHITE_HSV_LOWER
        if upper_hsv is None:
            upper_hsv = self.WHITE_HSV_UPPER
            
        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
        scaled = cv2.resize(mask, None, fx=scale_factor, fy=scale_factor,
                           interpolation=cv2.INTER_CUBIC)
        return scaled

    def preprocess_region(
        self,
        region: np.ndarray,
        method: str = "grayscale_scaled",
        scale_factor: float = 2.0,
        **kwargs
    ) -> np.ndarray:
        """
        Apply preprocessing to a region using the specified method.
        
        Args:
            region: Input image region
            method: Preprocessing method name
            scale_factor: Scale factor for upscaling
            **kwargs: Additional arguments for specific methods
            
        Returns:
            Preprocessed image region
        """
        method_map = {
            "grayscale": lambda r: self.preprocess_grayscale_scaled(r, 1.0),
            "grayscale_scaled": lambda r: self.preprocess_grayscale_scaled(r, scale_factor),
            "threshold": lambda r: self.preprocess_threshold(r, scale_factor, kwargs.get("threshold_value", 127)),
            "high_contrast": lambda r: self.preprocess_high_contrast(r, scale_factor),
            "inverted": lambda r: self.preprocess_inverted(r, scale_factor),
            "yellow_color_mask": lambda r: self.preprocess_yellow_color_mask(
                r, scale_factor, kwargs.get("lower_hsv"), kwargs.get("upper_hsv")
            ),
            "white_color_mask": lambda r: self.preprocess_white_color_mask(
                r, scale_factor, kwargs.get("lower_hsv"), kwargs.get("upper_hsv")
            ),
        }
        
        if method not in method_map:
            raise ValueError(f"Unknown preprocessing method: {method}. "
                           f"Available: {list(method_map.keys())}")
        
        return method_map[method](region)
