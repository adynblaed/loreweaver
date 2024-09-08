import os
import yaml
import json
import logging
import argparse
from enum import Enum
from typing import Dict, Any, List, Union
from pydantic import ValidationError, BaseModel
from datetime import datetime
from atoms import CharacterSheet

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Materializer:
    """
    A class to 'materialize' atomic narrative elements from data templates 
    and convert them into various formats for world-building and storytelling.
    """

    SUPPORTED_FORMATS = ['yaml', 'json', 'markdown']

    @staticmethod
    def load_yaml(file_path: str) -> dict:
        """
        Load a YAML file and return its contents as a dictionary.
        Args:
            file_path (str): Path to the YAML file.
        Returns:
            dict: The contents of the YAML file.
        Raises:
            ValueError: If there's an error parsing the YAML.
            IOError: If there's an error reading the file.
        """
        logger.info(f"Loading YAML from {file_path}")
        try:
            with open(file_path, 'r') as file:
                return yaml.safe_load(file)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {file_path}: {e}")
            raise ValueError(f"Error parsing YAML file: {e}")
        except IOError as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise IOError(f"Error reading file: {e}")

    @staticmethod
    def prepare_output_data(data: dict) -> dict:
        """
        Prepare the data for output, applying standardization and best practices.
        Args:
            data (dict): Input data.
        Returns:
            dict: Output data in a standardized format.
        """
        logger.debug("Preparing output data for serialization.")
        output = {
            "version": "1.0",
            "sheet_type": data.get("sheet_type", "unknown"),
            "last_modified": datetime.now().isoformat(),
        }
        for key, value in data.items():
            if isinstance(value, Enum):
                output[key] = value.name.upper()
            elif isinstance(value, (int, float, bool, str)):
                output[key] = value
            elif isinstance(value, list):
                output[key] = [Materializer.prepare_output_data(item) if isinstance(item, dict) else item for item in value]
            elif isinstance(value, dict):
                output[key] = Materializer.prepare_output_data(value)
            else:
                output[key] = str(value)
        return output

    @staticmethod
    def save_yaml(data: dict, file_path: str):
        """
        Save data to a YAML file.
        Args:
            data (dict): Data to save.
            file_path (str): Path to the YAML file.
        """
        logger.info(f"Saving YAML to {file_path}")
        try:
            with open(file_path, 'w') as file:
                yaml.dump(data, file, sort_keys=False, default_flow_style=False)
            logger.info(f"YAML saved successfully at {file_path}")
        except IOError as e:
            logger.error(f"Error saving YAML file {file_path}: {e}")
            raise IOError(f"Error saving YAML file: {e}")

    @staticmethod
    def save_json(data: dict, file_path: str):
        """
        Save data to a JSON file.
        Args:
            data (dict): Data to save.
            file_path (str): Path to the JSON file.
        """
        logger.info(f"Saving JSON to {file_path}")
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            logger.info(f"JSON saved successfully at {file_path}")
        except IOError as e:
            logger.error(f"Error saving JSON file {file_path}: {e}")
            raise IOError(f"Error saving JSON file: {e}")

    @staticmethod
    def save_markdown(data: dict, file_path: str):
        """
        Save data to a Markdown file.
        Args:
            data (dict): Data to save.
            file_path (str): Path to the Markdown file.
        """
        logger.info(f"Saving Markdown to {file_path}")
        try:
            with open(file_path, 'w') as file:
                file.write(Materializer.dict_to_md(data))
            logger.info(f"Markdown saved successfully at {file_path}")
        except IOError as e:
            logger.error(f"Error saving Markdown file {file_path}: {e}")
            raise IOError(f"Error saving Markdown file: {e}")

    @staticmethod
    def dict_to_md(d: Dict[str, Any], indent: int = 0) -> str:
        """
        Convert a dictionary into Markdown format.
        Args:
            d (Dict[str, Any]): Input dictionary.
            indent (int): Indentation level.
        Returns:
            str: Formatted Markdown string.
        """
        md = ""
        for key, value in d.items():
            md += f"{'  ' * indent}- **{key}**: "
            if isinstance(value, dict):
                md += "\n" + Materializer.dict_to_md(value, indent + 1)
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    md += "\n" + "  " * (indent + 1) + "- " + "\n  ".join(Materializer.dict_to_md(item, indent + 2) for item in value)
                else:
                    md += ", ".join(str(item) for item in value) + "\n"
            else:
                md += f"{value}\n"
        return md

    @classmethod
    def convert(cls, input_path: str, output_format: str, output_path: str):
        """
        Convert a YAML file to a specified format (JSON or Markdown).
        Args:
            input_path (str): Path to the YAML file.
            output_format (str): Output format ('json', 'markdown').
            output_path (str): Path to the output file.
        """
        if output_format not in cls.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported output format: {output_format}")

        # Load YAML input
        data = cls.load_yaml(input_path)

        # Prepare the output data
        output_data = cls.prepare_output_data(data)

        # Convert and save
        if output_format == 'json':
            cls.save_json(output_data, output_path)
        elif output_format == 'markdown':
            cls.save_markdown(output_data, output_path)

        logger.info(f"Conversion to {output_format} complete. Output saved to {output_path}")

def main():
    """
    Main function to handle command-line interface for the materializer tool.
    """
    parser = argparse.ArgumentParser(description="Convert YAML files into JSON or Markdown formats.")
    parser.add_argument("input", help="Path to the input YAML file")
    parser.add_argument("format", choices=['json', 'markdown'], help="Output format: 'json' or 'markdown'")
    parser.add_argument("--output", help="Where to save the converted file", required=True)

    args = parser.parse_args()

    try:
        Materializer.convert(args.input, args.format, args.output)
        print(f"Conversion complete! Your file is ready at {args.output}.")
    except Exception as e:
        print(f"Error: {str(e)}")
        logger.error(f"Conversion failed: {str(e)}")

if __name__ == "__main__":
    main()
