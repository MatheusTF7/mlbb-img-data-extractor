"""MLBB Player Data Extractor.

This module handles the extraction of player-specific data from
Mobile Legends Bang Bang end-game screenshots.
"""

import re
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

from ..preprocessor.image_processor import ImagePreprocessor
from ..regions import (
    Region, PlayerRowRegions, ALL_PLAYERS,
    RESULT_REGION, MY_TEAM_SCORE_REGION, ADVERSARY_SCORE_REGION, DURATION_REGION
)


class MedalType(Enum):
    """Medal types based on color."""
    GOLD = "GOLD"
    SILVER = "SILVER"
    BRONZE = "BRONZE"
    NONE = "NONE"


@dataclass
class PlayerStats:
    """Data class for player statistics."""
    nickname: str
    kills: int
    deaths: int
    assists: int
    gold: int
    medal: str
    ratio: float
    position: int  # 1-5 position in team


@dataclass
class MatchInfo:
    """Data class for match information."""
    result: str  # VICTORY or DEFEAT
    my_team_score: int
    adversary_team_score: int
    duration: str  # mm:ss format


@dataclass
class GameData:
    """Complete game data for a specific player."""
    nickname: str
    kills: int
    deaths: int
    assists: int
    gold: int
    medal: str
    ratio: float
    result: str
    my_team_score: int
    adversary_team_score: int
    duration: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "nickname": self.nickname,
            "kills": self.kills,
            "deaths": self.deaths,
            "assists": self.assists,
            "gold": self.gold,
            "medal": self.medal,
            "ratio": self.ratio,
            "result": self.result,
            "my_team_score": self.my_team_score,
            "adversary_team_score": self.adversary_team_score,
            "duration": self.duration,
        }


class MLBBExtractor:
    """
    Extracts player data from MLBB end-game screenshots.
    """

    # OCR configurations optimized for each field type
    OCR_CONFIGS = {
        "result": {
            "method": "threshold",
            "scale": 4,
            "psm": 7,
            "whitelist": "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        },
        "score": {
            "method": "grayscale_scaled",
            "scale": 3,
            "psm": 7,
            "whitelist": "0123456789"
        },
        "duration": {
            "method": "grayscale_scaled",
            "scale": 2,
            "psm": 7,
            "whitelist": "0123456789:"
        },
        "nickname": {
            "method": "grayscale_scaled",
            "scale": 2,
            "psm": 7,
            "whitelist": None  # Allow all characters for nicknames
        },
        "stats": {
            "method": "grayscale_scaled",
            "scale": 3,
            "psm": 7,
            "whitelist": "0123456789 "
        },
        "ratio": {
            "method": "yellow_color_mask",
            "scale": 5,
            "psm": 8,
            "whitelist": "0123456789."
        },
        "kills": {
            "method": "high_contrast",
            "scale": 4,
            "psm": 10,
            "whitelist": "0123456789"
        },
    }

    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize the MLBB Extractor.

        Args:
            tesseract_cmd: Optional path to tesseract executable
        """
        self.preprocessor = ImagePreprocessor()
        self.tesseract_cmd = tesseract_cmd
        
        # Import pytesseract here to allow custom cmd
        import pytesseract
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self.pytesseract = pytesseract

    def _extract_region(
        self, 
        image: np.ndarray, 
        region: Region
    ) -> np.ndarray:
        """Extract a region from the image using percentage coordinates."""
        height, width = image.shape[:2]
        x, y, w, h = region.to_pixels(width, height)
        return image[y:y+h, x:x+w]

    def _ocr_region(
        self,
        region_image: np.ndarray,
        config_name: str,
        custom_config: Optional[Dict] = None
    ) -> str:
        """
        Apply OCR to a region with optimized preprocessing.
        
        Args:
            region_image: Image region to process
            config_name: Name of predefined config to use
            custom_config: Optional custom configuration override
            
        Returns:
            Extracted text
        """
        config = custom_config or self.OCR_CONFIGS.get(config_name, self.OCR_CONFIGS["nickname"])
        
        # Preprocess the region
        processed = self.preprocessor.preprocess_region(
            region_image,
            method=config["method"],
            scale_factor=config["scale"]
        )
        
        # Build Tesseract config
        tesseract_config = f"--psm {config['psm']}"
        if config.get("whitelist"):
            tesseract_config += f" -c tessedit_char_whitelist={config['whitelist']}"
        
        # Run OCR
        try:
            text = self.pytesseract.image_to_string(processed, config=tesseract_config)
            return text.strip()
        except Exception as e:
            print(f"OCR error: {e}")
            return ""

    def extract_match_info(self, image: np.ndarray) -> MatchInfo:
        """
        Extract match-level information (result, scores, duration).
        
        Args:
            image: Full screenshot image
            
        Returns:
            MatchInfo object with match data
        """
        # Extract result (VICTORY/DEFEAT)
        result_region = self._extract_region(image, RESULT_REGION)
        result_text = self._ocr_region(result_region, "result")
        result = self._parse_result(result_text)
        
        # Extract my team score
        my_score_region = self._extract_region(image, MY_TEAM_SCORE_REGION)
        my_score_text = self._ocr_region(my_score_region, "score")
        my_score = self._parse_number(my_score_text, 0)
        
        # Extract adversary score
        adv_score_region = self._extract_region(image, ADVERSARY_SCORE_REGION)
        adv_score_text = self._ocr_region(adv_score_region, "score")
        adv_score = self._parse_number(adv_score_text, 0)
        
        # Extract duration
        duration_region = self._extract_region(image, DURATION_REGION)
        duration_text = self._ocr_region(duration_region, "duration")
        duration = self._parse_duration(duration_text)
        
        return MatchInfo(
            result=result,
            my_team_score=my_score,
            adversary_team_score=adv_score,
            duration=duration
        )

    def extract_player_nickname(
        self, 
        image: np.ndarray, 
        player_regions: PlayerRowRegions
    ) -> str:
        """Extract nickname from a player row."""
        nickname_region = self._extract_region(image, player_regions.nickname)
        nickname = self._ocr_region(nickname_region, "nickname")
        return self._clean_nickname(nickname)

    def extract_player_stats(
        self, 
        image: np.ndarray, 
        player_regions: PlayerRowRegions
    ) -> Tuple[int, int, int, int]:
        """
        Extract kills, deaths, assists, gold from player stats region.
        
        Uses multiple strategies to extract the 4 stat values.
        
        Returns:
            Tuple of (kills, deaths, assists, gold)
        """
        stats_region = self._extract_region(image, player_regions.stats)
        
        # Strategy 1: Try PSM 6 (uniform block) which sometimes preserves spaces
        processed = self.preprocessor.preprocess_grayscale_scaled(stats_region, 3)
        text1 = self.pytesseract.image_to_string(
            processed, 
            config="--psm 6 -c tessedit_char_whitelist=0123456789 "
        ).strip()
        
        numbers = re.findall(r'\d+', text1)
        if len(numbers) >= 4:
            return (int(numbers[0]), int(numbers[1]), int(numbers[2]), int(numbers[3]))
        
        # Strategy 2: Try with different preprocessing (inverted)
        inverted = self.preprocessor.preprocess_inverted(stats_region, 3)
        text2 = self.pytesseract.image_to_string(
            inverted, 
            config="--psm 6 -c tessedit_char_whitelist=0123456789 "
        ).strip()
        
        numbers = re.findall(r'\d+', text2)
        if len(numbers) >= 4:
            return (int(numbers[0]), int(numbers[1]), int(numbers[2]), int(numbers[3]))
        
        # Strategy 3: Use image_to_data to get word bounding boxes
        data = self.pytesseract.image_to_data(processed, output_type=self.pytesseract.Output.DICT)
        words = [w for w in data['text'] if w.strip()]
        word_numbers = []
        for w in words:
            digits = ''.join(filter(str.isdigit, w))
            if digits:
                word_numbers.append(int(digits))
        
        if len(word_numbers) >= 4:
            return (word_numbers[0], word_numbers[1], word_numbers[2], word_numbers[3])
        
        # Strategy 4: Smart parse of concatenated string
        # Use the best text (one without duplication)
        best_text = text1 if text1 else text2
        all_digits = ''.join(filter(str.isdigit, best_text))
        
        if len(all_digits) >= 7:
            return self._parse_concatenated_stats_smart(all_digits)
        
        # Strategy 5: If we have 3 word_numbers from Strategy 3, try to split the first one
        # E.g., ['2410', '6', '28311'] -> try splitting '2410' into kills and deaths
        if len(word_numbers) == 3:
            first = str(word_numbers[0])
            # Try to split first number into K and D
            if len(first) >= 2:
                # Try splits: 1+rest, 2+rest
                for split_at in [1, 2]:
                    if split_at < len(first):
                        k = int(first[:split_at])
                        d = int(first[split_at:])
                        a = word_numbers[1]
                        gold = word_numbers[2]
                        
                        if 0 <= k <= 50 and 0 <= d <= 30 and 0 <= a <= 50 and gold >= 1000:
                            return (k, d, a, gold)
        
        return (0, 0, 0, 0)

    def _parse_concatenated_stats(self, stats_text: str) -> Tuple[int, int, int, int]:
        """
        Parse stats from a concatenated OCR string.
        Fallback method when individual extraction fails.
        """
        # Remove all non-digit characters
        digits_only = ''.join(filter(str.isdigit, stats_text))
        
        if not digits_only or len(digits_only) < 7:
            return (0, 0, 0, 0)
        
        # Try to find spaces first (ideal case)
        numbers = re.findall(r'\d+', stats_text)
        
        if len(numbers) >= 4:
            return (
                int(numbers[0]),
                int(numbers[1]),
                int(numbers[2]),
                int(numbers[3])
            )
        
        return self._parse_concatenated_stats_smart(digits_only)

    def _parse_concatenated_stats_smart(self, digits: str) -> Tuple[int, int, int, int]:
        """
        Smart parsing of concatenated stats knowing gold is 4-5 digits.
        
        Format: K D A Gold where:
        - K, D, A are 1-2 digits each
        - Gold is 4-5 digits (typically 5000-30000)
        """
        if len(digits) < 7:
            return (0, 0, 0, 0)
        
        # Gold is the last 5 digits (or 4 if total length doesn't allow 5)
        # We need at least 3 digits for K+D+A (minimum 1+1+1)
        
        best_result = (0, 0, 0, 0)
        best_gold_reasonableness = -1
        
        # Try gold lengths of 5 and 4 digits
        for gold_len in [5, 4]:
            if len(digits) < gold_len + 3:
                continue
            
            gold_str = digits[-gold_len:]
            kda_str = digits[:-gold_len]
            
            gold = int(gold_str)
            
            # Gold should be in reasonable range (4000-35000 typical)
            if not (3000 <= gold <= 40000):
                continue
            
            # Try all valid KDA parses
            kda = self._parse_kda_all_combinations(kda_str)
            
            if kda:
                # Score based on gold reasonableness
                gold_score = 10 if (8000 <= gold <= 30000) else 5
                
                if gold_score > best_gold_reasonableness:
                    best_gold_reasonableness = gold_score
                    best_result = (kda[0], kda[1], kda[2], gold)
        
        return best_result

    def _parse_kda_all_combinations(self, kda_str: str) -> Optional[Tuple[int, int, int]]:
        """
        Try all valid KDA parse combinations and return the most reasonable one.
        """
        length = len(kda_str)
        
        if length < 3:
            return None
        
        valid_parses = []
        
        # Generate all possible patterns
        for k_len in range(1, min(3, length-1)):
            for d_len in range(1, min(3, length-k_len)):
                a_len = length - k_len - d_len
                if not (1 <= a_len <= 3):
                    continue
                
                try:
                    k = int(kda_str[:k_len])
                    d = int(kda_str[k_len:k_len+d_len])
                    a = int(kda_str[k_len+d_len:])
                    
                    if 0 <= k <= 50 and 0 <= d <= 30 and 0 <= a <= 50:
                        # Score this parse
                        score = 0
                        
                        # Prefer when d < k + a (deaths usually less than kills+assists)
                        if d < k + a:
                            score += 10
                        
                        # Prefer when k and a have similar magnitude
                        if k > 0 and a > 0:
                            ratio = max(k, a) / min(k, a)
                            if ratio < 10:
                                score += 5
                            if ratio < 5:
                                score += 3
                        
                        # Prefer balanced digit lengths (2,2,1 or 2,1,2 better than 2,1,1)
                        digit_variance = abs(k_len - d_len) + abs(d_len - a_len)
                        score += max(0, 5 - digit_variance * 2)
                        
                        # Prefer 2-digit values for all when total length is 6
                        if length == 6 and k_len == d_len == a_len == 2:
                            score += 5
                        
                        # For length 5: prefer (2,2,1) pattern
                        if length == 5 and k_len == 2 and d_len == 2 and a_len == 1:
                            score += 5
                        
                        # Penalize d=1 when d_len=1 and other numbers are multi-digit
                        # This handles cases like "24106" where (24,1,6) vs (24,10,6)
                        if d_len == 1 and d <= 1 and (k >= 10 or a >= 10):
                            score -= 5
                        
                        # Prefer deaths in typical range (5-15 is very common)
                        if 5 <= d <= 15:
                            score += 3
                        
                        valid_parses.append((score, k, d, a))
                except ValueError:
                    continue
        
        if valid_parses:
            # Return the highest scoring parse
            valid_parses.sort(reverse=True)
            _, k, d, a = valid_parses[0]
            return (k, d, a)
        
        return None

    def _parse_kda_string(self, kda_str: str) -> Optional[Tuple[int, int, int]]:
        """
        Parse K/D/A from a continuous string.
        Best-effort fallback when individual extraction fails.
        """
        length = len(kda_str)
        
        if length < 3:
            return None
        
        # Generate all possible patterns
        patterns = []
        for k_len in range(1, min(3, length-1)):
            for d_len in range(1, min(3, length-k_len)):
                a_len = length - k_len - d_len
                if 1 <= a_len <= 3:
                    patterns.append((k_len, d_len, a_len))
        
        # Find first valid parse
        for p in patterns:
            try:
                k = int(kda_str[:p[0]])
                d = int(kda_str[p[0]:p[0]+p[1]])
                a = int(kda_str[p[0]+p[1]:])
                
                if 0 <= k <= 50 and 0 <= d <= 30 and 0 <= a <= 50:
                    return (k, d, a)
            except ValueError:
                continue
        
        return None

    def extract_player_ratio(
        self, 
        image: np.ndarray, 
        player_regions: PlayerRowRegions
    ) -> float:
        """Extract performance ratio from player row."""
        ratio_region = self._extract_region(image, player_regions.ratio)
        
        # Try grayscale with high scale first (most reliable based on tests)
        processed = self.preprocessor.preprocess_grayscale_scaled(ratio_region, 6)
        tesseract_config = "--psm 8 -c tessedit_char_whitelist=0123456789."
        ratio_text = self.pytesseract.image_to_string(processed, config=tesseract_config).strip()
        
        result = self._parse_float(ratio_text, 0.0)
        
        if result > 0:
            return result
        
        # Fallback: try yellow color mask for gold badges
        ratio_text = self._ocr_region(ratio_region, "ratio")
        
        return self._parse_float(ratio_text, 0.0)

    def extract_player_medal(
        self, 
        image: np.ndarray, 
        player_regions: PlayerRowRegions
    ) -> str:
        """
        Detect medal color (GOLD, SILVER, BRONZE) from player row.
        Uses color analysis instead of OCR.
        """
        medal_region = self._extract_region(image, player_regions.medal)
        return self._detect_medal_color(medal_region)

    def _detect_medal_color(self, region: np.ndarray) -> str:
        """Detect medal type based on dominant color."""
        if region.size == 0:
            return MedalType.NONE.value
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        
        # Define color ranges
        # Gold: yellowish
        gold_lower = np.array([15, 80, 120])
        gold_upper = np.array([35, 255, 255])
        
        # Silver: low saturation, high value
        silver_lower = np.array([0, 0, 150])
        silver_upper = np.array([180, 50, 255])
        
        # Bronze: orange-brown
        bronze_lower = np.array([8, 80, 80])
        bronze_upper = np.array([20, 255, 200])
        
        # Count pixels for each color
        gold_mask = cv2.inRange(hsv, gold_lower, gold_upper)
        silver_mask = cv2.inRange(hsv, silver_lower, silver_upper)
        bronze_mask = cv2.inRange(hsv, bronze_lower, bronze_upper)
        
        gold_pixels = cv2.countNonZero(gold_mask)
        silver_pixels = cv2.countNonZero(silver_mask)
        bronze_pixels = cv2.countNonZero(bronze_mask)
        
        # Determine medal type
        max_pixels = max(gold_pixels, silver_pixels, bronze_pixels)
        
        if max_pixels < 50:  # Minimum threshold
            return MedalType.NONE.value
        
        if max_pixels == gold_pixels:
            return MedalType.GOLD.value
        elif max_pixels == silver_pixels:
            return MedalType.SILVER.value
        else:
            return MedalType.BRONZE.value

    def find_player_by_nickname(
        self, 
        image: np.ndarray, 
        target_nickname: str
    ) -> Optional[int]:
        """
        Find a player's position by nickname.
        
        Args:
            image: Full screenshot image
            target_nickname: Nickname to search for
            
        Returns:
            Player position (0-4) or None if not found
        """
        target_lower = target_nickname.lower().strip()
        
        for idx, player_regions in enumerate(ALL_PLAYERS):
            nickname = self.extract_player_nickname(image, player_regions)
            nickname_lower = nickname.lower().strip()
            
            # Check for exact match or partial match
            if target_lower in nickname_lower or nickname_lower in target_lower:
                return idx
            
            # Check similarity (fuzzy match)
            if self._similar_names(target_lower, nickname_lower):
                return idx
        
        return None

    def _similar_names(self, name1: str, name2: str, threshold: float = 0.6) -> bool:
        """Check if two names are similar using simple ratio."""
        if not name1 or not name2:
            return False
        
        # Simple character overlap ratio
        set1, set2 = set(name1), set(name2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return False
        
        return (intersection / union) >= threshold

    def extract_player_data(
        self, 
        image: np.ndarray, 
        player_index: int
    ) -> PlayerStats:
        """
        Extract all data for a specific player position.
        
        Args:
            image: Full screenshot image
            player_index: Player position (0-4)
            
        Returns:
            PlayerStats object with all player data
        """
        player_regions = ALL_PLAYERS[player_index]
        
        nickname = self.extract_player_nickname(image, player_regions)
        kills, deaths, assists, gold = self.extract_player_stats(image, player_regions)
        ratio = self.extract_player_ratio(image, player_regions)
        medal = self.extract_player_medal(image, player_regions)
        
        return PlayerStats(
            nickname=nickname,
            kills=kills,
            deaths=deaths,
            assists=assists,
            gold=gold,
            medal=medal,
            ratio=ratio,
            position=player_index + 1
        )

    def extract_game_data(
        self, 
        image_path: str, 
        player_nickname: str
    ) -> Optional[GameData]:
        """
        Extract complete game data for a specific player.
        
        Args:
            image_path: Path to the screenshot image
            player_nickname: Nickname of the player to find
            
        Returns:
            GameData object or None if player not found
        """
        # Load image
        image = self.preprocessor.load_image(image_path)
        
        # Find player position
        player_index = self.find_player_by_nickname(image, player_nickname)
        
        if player_index is None:
            print(f"Player '{player_nickname}' not found in screenshot")
            return None
        
        # Extract match info
        match_info = self.extract_match_info(image)
        
        # Extract player data
        player_stats = self.extract_player_data(image, player_index)
        
        return GameData(
            nickname=player_stats.nickname,
            kills=player_stats.kills,
            deaths=player_stats.deaths,
            assists=player_stats.assists,
            gold=player_stats.gold,
            medal=player_stats.medal,
            ratio=player_stats.ratio,
            result=match_info.result,
            my_team_score=match_info.my_team_score,
            adversary_team_score=match_info.adversary_team_score,
            duration=match_info.duration
        )

    def extract_all_players(
        self, 
        image_path: str
    ) -> List[Dict[str, Any]]:
        """
        Extract data for all 5 players on my team.
        
        Args:
            image_path: Path to the screenshot image
            
        Returns:
            List of dictionaries with player data
        """
        image = self.preprocessor.load_image(image_path)
        match_info = self.extract_match_info(image)
        
        results = []
        for idx in range(5):
            player_stats = self.extract_player_data(image, idx)
            data = {
                "nickname": player_stats.nickname,
                "kills": player_stats.kills,
                "deaths": player_stats.deaths,
                "assists": player_stats.assists,
                "gold": player_stats.gold,
                "medal": player_stats.medal,
                "ratio": player_stats.ratio,
                "position": player_stats.position,
                "result": match_info.result,
                "my_team_score": match_info.my_team_score,
                "adversary_team_score": match_info.adversary_team_score,
                "duration": match_info.duration
            }
            results.append(data)
        
        return results

    # =========================================================================
    # Helper parsing methods
    # =========================================================================

    def _parse_result(self, text: str) -> str:
        """Parse game result from text."""
        text_upper = text.upper()
        if "VICTORY" in text_upper or "VICTOR" in text_upper or "WIN" in text_upper:
            return "VICTORY"
        elif "DEFEAT" in text_upper or "LOSE" in text_upper or "LOSS" in text_upper:
            return "DEFEAT"
        return "UNKNOWN"

    def _parse_number(self, text: str, default: int = 0) -> int:
        """Parse integer from text."""
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        return default

    def _parse_float(self, text: str, default: float = 0.0) -> float:
        """Parse float from text."""
        # Match patterns like "9.1", "10.0", ".5"
        match = re.search(r'(\d+\.?\d*|\.\d+)', text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return default

    def _parse_duration(self, text: str) -> str:
        """Parse duration in mm:ss format."""
        # Try to find mm:ss pattern
        match = re.search(r'(\d{1,2}):(\d{2})', text)
        if match:
            return f"{match.group(1)}:{match.group(2)}"
        
        # Try to reconstruct from numbers
        numbers = re.findall(r'\d+', text)
        if len(numbers) >= 2:
            return f"{numbers[0]}:{numbers[1].zfill(2)}"
        
        return "00:00"

    def _clean_nickname(self, text: str) -> str:
        """Clean extracted nickname."""
        # Remove common OCR artifacts
        cleaned = text.strip()
        # Remove leading/trailing special characters except common ones in nicknames
        cleaned = re.sub(r'^[@#$%^&*()_+=\[\]{}|\\<>/?`~]+', '', cleaned)
        cleaned = re.sub(r'[@#$%^&*()_+=\[\]{}|\\<>/?`~]+$', '', cleaned)
        # Remove newlines
        cleaned = cleaned.replace('\n', '').replace('\r', '')
        return cleaned.strip()


# Import cv2 at module level for medal detection
import cv2
