"""Data parsing module for structuring extracted text."""

import re
from typing import Dict, List, Any, Optional
import pandas as pd


class DataParser:
    """
    Parses extracted text and structures it into meaningful data.
    Handles Mobile Legends game statistics parsing.
    """

    def __init__(self):
        """Initialize the DataParser."""
        pass

    def parse_kda(self, text: str) -> Dict[str, int]:
        """
        Parse K/D/A (Kills/Deaths/Assists) from text.

        Args:
            text: Text containing K/D/A information

        Returns:
            Dictionary with kills, deaths, and assists
        """
        # Pattern: "10/2/15" or "10-2-15"
        pattern = r"(\d+)[/-](\d+)[/-](\d+)"
        match = re.search(pattern, text)
        
        if match:
            return {
                "kills": int(match.group(1)),
                "deaths": int(match.group(2)),
                "assists": int(match.group(3)),
            }
        
        return {"kills": 0, "deaths": 0, "assists": 0}

    def parse_gold(self, text: str) -> float:
        """
        Parse gold amount from text.

        Args:
            text: Text containing gold information

        Returns:
            Gold amount as float
        """
        # Pattern: "12.5k" or "12500" or "12.5K gold"
        pattern = r"(\d+\.?\d*)\s*([kK])?"
        match = re.search(pattern, text)
        
        if match:
            value = float(match.group(1))
            # If 'k' or 'K' is present, multiply by 1000
            if match.group(2):
                value *= 1000
            return value
        
        return 0.0

    def parse_damage(self, text: str) -> float:
        """
        Parse damage amount from text.

        Args:
            text: Text containing damage information

        Returns:
            Damage amount as float
        """
        # Similar to gold parsing
        pattern = r"(\d+\.?\d*)\s*([kK])?"
        match = re.search(pattern, text)
        
        if match:
            value = float(match.group(1))
            if match.group(2):
                value *= 1000
            return value
        
        return 0.0

    def parse_player_name(self, text: str) -> str:
        """
        Extract player name from text.

        Args:
            text: Text containing player name

        Returns:
            Cleaned player name
        """
        # Remove special characters and extra whitespace
        name = re.sub(r"[^\w\s\-]", "", text)
        name = " ".join(name.split())
        return name

    def parse_hero_name(self, text: str) -> str:
        """
        Extract hero name from text.

        Args:
            text: Text containing hero name

        Returns:
            Cleaned hero name
        """
        # Remove special characters and extra whitespace
        hero = re.sub(r"[^\w\s]", "", text)
        hero = " ".join(hero.split())
        return hero

    def parse_game_result(self, text: str) -> str:
        """
        Determine game result (Victory/Defeat) from text.

        Args:
            text: Text containing game result

        Returns:
            "Victory" or "Defeat" or "Unknown"
        """
        text_lower = text.lower()
        
        if "victory" in text_lower or "win" in text_lower:
            return "Victory"
        elif "defeat" in text_lower or "lose" in text_lower or "loss" in text_lower:
            return "Defeat"
        
        return "Unknown"

    def parse_game_duration(self, text: str) -> Optional[int]:
        """
        Parse game duration in seconds from text.

        Args:
            text: Text containing duration (e.g., "15:30")

        Returns:
            Duration in seconds or None
        """
        # Pattern: "15:30" or "15m 30s"
        pattern1 = r"(\d+):(\d+)"
        pattern2 = r"(\d+)\s*m(?:in)?\s*(\d+)\s*s(?:ec)?"
        
        match = re.search(pattern1, text)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            return minutes * 60 + seconds
        
        match = re.search(pattern2, text)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            return minutes * 60 + seconds
        
        return None

    def structure_player_data(
        self, extracted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Structure raw extracted data into organized player statistics.

        Args:
            extracted_data: Raw extracted data from OCR

        Returns:
            Structured player data dictionary
        """
        structured = {
            "player_name": self.parse_player_name(
                extracted_data.get("player_name", "")
            ),
            "hero_name": self.parse_hero_name(
                extracted_data.get("hero_name", "")
            ),
            "game_result": self.parse_game_result(
                extracted_data.get("game_result", "")
            ),
            "duration": self.parse_game_duration(
                extracted_data.get("duration", "")
            ),
        }
        
        # Parse K/D/A if present
        if "kda" in extracted_data:
            kda = self.parse_kda(extracted_data["kda"])
            structured.update(kda)
        else:
            # Set defaults if no K/D/A data
            structured.update({"kills": 0, "deaths": 0, "assists": 0})
        
        # Parse individual stats
        if "gold" in extracted_data:
            structured["gold"] = self.parse_gold(extracted_data["gold"])
        else:
            structured["gold"] = 0.0
        
        if "damage" in extracted_data:
            structured["damage"] = self.parse_damage(extracted_data["damage"])
        else:
            structured["damage"] = 0.0
        
        return structured

    def create_dataframe(
        self, player_data_list: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Create a Pandas DataFrame from a list of player data.

        Args:
            player_data_list: List of player data dictionaries

        Returns:
            Pandas DataFrame with structured data
        """
        if not player_data_list:
            return pd.DataFrame()
        
        df = pd.DataFrame(player_data_list)
        
        # Ensure proper data types with error handling
        if "kills" in df.columns:
            df["kills"] = pd.to_numeric(df["kills"], errors="coerce").fillna(0).astype(int)
        if "deaths" in df.columns:
            df["deaths"] = pd.to_numeric(df["deaths"], errors="coerce").fillna(0).astype(int)
        if "assists" in df.columns:
            df["assists"] = pd.to_numeric(df["assists"], errors="coerce").fillna(0).astype(int)
        if "gold" in df.columns:
            df["gold"] = pd.to_numeric(df["gold"], errors="coerce").fillna(0.0).astype(float)
        if "damage" in df.columns:
            df["damage"] = pd.to_numeric(df["damage"], errors="coerce").fillna(0.0).astype(float)
        
        return df
