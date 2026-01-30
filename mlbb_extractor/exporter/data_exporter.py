"""Data export module for saving structured data."""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional


class DataExporter:
    """
    Handles exporting structured data to various formats (CSV, JSON).
    """

    def __init__(self, output_dir: str = "output"):
        """
        Initialize the DataExporter.

        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_to_csv(
        self,
        data: pd.DataFrame,
        filename: str = "game_stats.csv",
        index: bool = False,
    ) -> str:
        """
        Export data to CSV format.

        Args:
            data: Pandas DataFrame to export
            filename: Output filename
            index: Whether to include index in CSV

        Returns:
            Path to the saved CSV file
        """
        output_path = self.output_dir / filename
        data.to_csv(output_path, index=index)
        return str(output_path)

    def export_to_json(
        self,
        data: Any,
        filename: str = "game_stats.json",
        pretty: bool = True,
    ) -> str:
        """
        Export data to JSON format.

        Args:
            data: Data to export (dict, list, or DataFrame)
            filename: Output filename
            pretty: Whether to use pretty printing

        Returns:
            Path to the saved JSON file
        """
        output_path = self.output_dir / filename
        
        # Convert DataFrame to dict if needed
        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient="records")
        
        with open(output_path, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
        
        return str(output_path)

    def export_to_excel(
        self,
        data: pd.DataFrame,
        filename: str = "game_stats.xlsx",
        sheet_name: str = "Game Stats",
    ) -> str:
        """
        Export data to Excel format.

        Args:
            data: Pandas DataFrame to export
            filename: Output filename
            sheet_name: Name of the Excel sheet

        Returns:
            Path to the saved Excel file
        """
        output_path = self.output_dir / filename
        data.to_excel(output_path, sheet_name=sheet_name, index=False)
        return str(output_path)

    def append_to_csv(
        self,
        data: pd.DataFrame,
        filename: str = "game_stats.csv",
        index: bool = False,
    ) -> str:
        """
        Append data to an existing CSV file or create new one.

        Args:
            data: Pandas DataFrame to append
            filename: Output filename
            index: Whether to include index in CSV

        Returns:
            Path to the CSV file
        """
        output_path = self.output_dir / filename
        
        # Check if file exists
        if output_path.exists():
            # Read existing data
            existing_data = pd.read_csv(output_path)
            # Concatenate with new data
            combined_data = pd.concat([existing_data, data], ignore_index=True)
            combined_data.to_csv(output_path, index=index)
        else:
            # Create new file
            data.to_csv(output_path, index=index)
        
        return str(output_path)

    def export_multiple_formats(
        self,
        data: pd.DataFrame,
        base_filename: str = "game_stats",
        formats: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """
        Export data to multiple formats at once.

        Args:
            data: Pandas DataFrame to export
            base_filename: Base name for output files (without extension)
            formats: List of formats to export ('csv', 'json', 'excel')
                    If None, exports to all formats

        Returns:
            Dictionary mapping format to file path
        """
        if formats is None:
            formats = ["csv", "json"]
        
        results = {}
        
        if "csv" in formats:
            results["csv"] = self.export_to_csv(
                data, f"{base_filename}.csv"
            )
        
        if "json" in formats:
            results["json"] = self.export_to_json(
                data, f"{base_filename}.json"
            )
        
        if "excel" in formats:
            results["excel"] = self.export_to_excel(
                data, f"{base_filename}.xlsx"
            )
        
        return results

    def save_raw_text(
        self, text: str, filename: str = "raw_text.txt"
    ) -> str:
        """
        Save raw extracted text to a file.

        Args:
            text: Raw text to save
            filename: Output filename

        Returns:
            Path to the saved file
        """
        output_path = self.output_dir / filename
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        return str(output_path)
