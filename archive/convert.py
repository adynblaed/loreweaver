import yaml
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Union, List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class YAMLConverter:
    def __init__(self, output_format: str = 'md'):
        self.output_format = output_format

    def load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file and return as dictionary."""
        try:
            with file_path.open('r') as file:
                return yaml.safe_load(file)
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML file {file_path}: {e}")
            raise

    def yaml_to_markdown(self, data: Dict[str, Any], level: int = 0) -> str:
        """Convert YAML data to Markdown format."""
        markdown = ""
        for key, value in data.items():
            markdown += "#" * (level + 1) + f" {key}\n\n"
            if isinstance(value, dict):
                markdown += self.yaml_to_markdown(value, level + 1)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        markdown += self.yaml_to_markdown(item, level + 1)
                    else:
                        markdown += f"- {item}\n"
                markdown += "\n"
            else:
                markdown += f"{value}\n\n"
        return markdown

    def convert_file(self, input_path: Path, output_dir: Path) -> None:
        """Convert a single YAML file to the specified format."""
        data = self.load_yaml(input_path)
        output_file = output_dir / f"{input_path.stem}.{self.output_format}"
        
        if self.output_format == 'md':
            content = self.yaml_to_markdown(data)
        elif self.output_format == 'json':
            content = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported output format: {self.output_format}")
        
        output_file.write_text(content)
        logging.info(f"Created {output_file}")

    def process_path(self, input_path: Path, output_dir: Path) -> None:
        """Process input path, whether it's a file or directory."""
        output_dir.mkdir(parents=True, exist_exist=True)
        
        if input_path.is_file():
            if input_path.suffix.lower() in ['.yaml', '.yml']:
                self.convert_file(input_path, output_dir)
            else:
                logging.warning(f"Skipping non-YAML file: {input_path}")
        elif input_path.is_dir():
            for yaml_file in input_path.glob('**/*.yaml'):
                self.convert_file(yaml_file, output_dir)
            for yaml_file in input_path.glob('**/*.yml'):
                self.convert_file(yaml_file, output_dir)
        else:
            logging.error(f"Invalid input path: {input_path}")

class CLIHandler:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Convert YAML files to Markdown or JSON.")
        self.parser.add_argument("input_path", help="YAML file or directory containing YAML files")
        self.parser.add_argument("-o", "--output", help="Output directory (default: current directory)", default=".")
        self.parser.add_argument("-f", "--format", choices=['md', 'json'], default='md', help="Output format (default: md)")

    def parse_args(self):
        return self.parser.parse_args()

def main():
    cli_handler = CLIHandler()
    args = cli_handler.parse_args()

    input_path = Path(args.input_path)
    output_dir = Path(args.output)
    
    converter = YAMLConverter(output_format=args.format)
    
    try:
        converter.process_path(input_path, output_dir)
        logging.info("Conversion completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()