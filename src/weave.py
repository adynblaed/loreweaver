"""
src/lore/weave.py

Loreweaver: A tool for generating and populating worldbuilding templates.

This script generates YAML and JSON templates from Python data models defined in a source file,
and can use a local vLLM server to fill these templates with content based on user input.

Usage:
    python src/weave.py src/lore/core.py --yaml
    python src/weave.py src/lore/core.py --json
    python src/weave.py src/lore/core.py --json --prompt "Your prompt here"

Author: Adyn Blaed
Version: 1.6.0
"""

import ast
import os
import yaml
import json
import argparse
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum, auto
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the vLLM server URL and API key from environment variables
VLLM_SERVER_URL = os.getenv("VLLM_SERVER_URL", "http://localhost:8000/v1")
VLLM_API_KEY = os.getenv("VLLM_API_KEY", "token-abc123")

# Initialize the OpenAI client with vLLM server settings
client = OpenAI(
    base_url=VLLM_SERVER_URL,
    api_key=VLLM_API_KEY,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
DEFAULT_OUTPUT_DIR = Path("lore/templates")
SUPPORTED_TYPES = ['str', 'int', 'float', 'bool', 'UUID', 'datetime', 'LocalizedString']
VLLM_MODEL = os.getenv("VLLM_MODEL", "NousResearch/Meta-Llama-3-8B-Instruct")

# Constants
DEFAULT_OUTPUT_DIR = Path("lore/templates")
SUPPORTED_TYPES = ['str', 'int', 'float', 'bool', 'UUID', 'datetime', 'LocalizedString']

class OutputType(Enum):
    """Enumeration of supported output types."""
    SHEETS = "sheets"
    SINGLE = "single"

class ProcessType(Enum):
    """Enumeration of supported processing types."""
    FULL = "full"
    BASE = "base"

@dataclass
class FieldInfo:
    """Represents information about a field in a data model."""
    name: str
    type: str
    default: Optional[Any] = None
    description: Optional[str] = None

@dataclass
class ModelInfo:
    """Represents information about a data model."""
    fields: List[FieldInfo] = field(default_factory=list)
    bases: List[str] = field(default_factory=list)
    description: Optional[str] = None

def parse_lorecore(filename: Path) -> Dict[str, ModelInfo]:
    """
    Parse the input file and extract model information.

    Args:
        filename (Path): Path to the input file.

    Returns:
        Dict[str, ModelInfo]: Dictionary of model names to their information.

    Raises:
        IOError: If the file cannot be read.
        SyntaxError: If the file contains invalid Python syntax.
    """
    try:
        with open(filename, 'r') as file:
            tree = ast.parse(file.read())
    except IOError as e:
        logger.error(f"Failed to read file {filename}: {e}")
        raise
    except SyntaxError as e:
        logger.error(f"Invalid Python syntax in {filename}: {e}")
        raise

    models = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            fields = []
            class_description = ast.get_docstring(node)
            for child in node.body:
                if isinstance(child, ast.AnnAssign):
                    field_name = child.target.id
                    field_type = get_field_type(child.annotation)
                    default = get_default_value(child)
                    field_description = get_field_description(child)
                    fields.append(FieldInfo(field_name, field_type, default, field_description))
            models[class_name] = ModelInfo(
                fields=fields,
                bases=[base.id for base in node.bases if isinstance(base, ast.Name)],
                description=class_description
            )

    return models

def get_field_type(annotation: ast.AST) -> str:
    """
    Extract the field type from an AST annotation.

    Args:
        annotation (ast.AST): The AST node representing the type annotation.

    Returns:
        str: A string representation of the field type.
    """
    if isinstance(annotation, ast.Name):
        return annotation.id
    elif isinstance(annotation, ast.Subscript):
        return f"{annotation.value.id}[{get_field_type(annotation.slice)}]"
    return str(annotation)

def get_default_value(node: ast.AnnAssign) -> Optional[Any]:
    """
    Extract the default value from an AST node.

    Args:
        node (ast.AnnAssign): The AST node representing the field assignment.

    Returns:
        Optional[Any]: The default value if present, None otherwise.
    """
    if node.value and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'Field':
        for kw in node.value.keywords:
            if kw.arg in ('default_factory', 'default'):
                return get_value_representation(kw.value)
    return None

def get_value_representation(node: ast.AST) -> str:
    """
    Get a string representation of an AST node's value.

    Args:
        node (ast.AST): The AST node representing a value.

    Returns:
        str: A string representation of the value.
    """
    if isinstance(node, ast.Name):
        return f"<{node.id}>"
    elif isinstance(node, ast.Attribute):
        return f"<{node.attr}>"
    elif isinstance(node, ast.Constant):
        return node.value
    return "<complex value>"

def get_field_description(node: ast.AnnAssign) -> Optional[str]:
    """
    Extract the field description from an AST node.

    Args:
        node (ast.AnnAssign): The AST node representing the field assignment.

    Returns:
        Optional[str]: The field description if present, None otherwise.
    """
    if node.value and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'Field':
        for kw in node.value.keywords:
            if kw.arg == 'description':
                if isinstance(kw.value, ast.Constant):
                    return kw.value.value
    return None

def create_template(model_name: str, model_info: ModelInfo, all_models: Dict[str, ModelInfo], process_type: ProcessType) -> Dict[str, Any]:
    """
    Create a template for a given model.

    Args:
        model_name (str): Name of the model.
        model_info (ModelInfo): Information about the model.
        all_models (Dict[str, ModelInfo]): Dictionary of all models.
        process_type (ProcessType): Type of processing to apply.

    Returns:
        Dict[str, Any]: Template as a dictionary.
    """
    template_dict = {model_name: {}}

    if process_type == ProcessType.FULL:
        if model_info.description:
            template_dict[model_name]['__description__'] = model_info.description

    # Include fields from base classes
    for base in model_info.bases:
        if base in all_models:
            base_dict = create_template(base, all_models[base], all_models, process_type)
            template_dict[model_name].update(base_dict[base])

    for field in model_info.fields:
        if field.default is not None:
            template_dict[model_name][field.name] = field.default
        elif field.type in SUPPORTED_TYPES:
            template_dict[model_name][field.name] = f"<{field.type}>"
        elif field.type.startswith('List'):
            template_dict[model_name][field.name] = []
        elif field.type.startswith('Dict'):
            template_dict[model_name][field.name] = {}
        else:
            template_dict[model_name][field.name] = f"<{field.type}>"

        if process_type == ProcessType.FULL and field.description:
            template_dict[model_name][f"{field.name}__description__"] = field.description

    return template_dict

def generate_templates(input_file: Path, output_dir: Path, format: str) -> Path:
    """
    Generate templates from the input file for all processing types and output types.

    Args:
        input_file (Path): Path to the input file.
        output_dir (Path): Path to the output directory.
        format (str): Output format ('yaml' or 'json').

    Returns:
        Path: Path to the generated single file output.

    Raises:
        Exception: If an error occurs during template generation.
    """
    try:
        models = parse_lorecore(input_file)

        for process_type in ProcessType:
            process_dir = output_dir / format / process_type.value
            process_dir.mkdir(parents=True, exist_ok=True)

            # Generate single file output
            all_template_dict = {}
            for model_name, model_info in models.items():
                all_template_dict.update(create_template(model_name, model_info, models, process_type))

            if format == 'yaml':
                content = yaml.dump(all_template_dict, sort_keys=False, default_flow_style=False)
                file_extension = 'yaml'
            else:  # json
                content = json.dumps(all_template_dict, indent=2)
                file_extension = 'json'

            single_output_file = process_dir / f"{input_file.stem}_all.{file_extension}"
            with open(single_output_file, 'w') as file:
                file.write(content)
            logger.info(f"Generated single {format.upper()} file: {single_output_file}")

            # Generate multiple files output
            sheets_dir = process_dir / "sheets"
            sheets_dir.mkdir(parents=True, exist_ok=True)
            for model_name, model_info in models.items():
                template_dict = create_template(model_name, model_info, models, process_type)
                if format == 'yaml':
                    content = yaml.dump(template_dict, sort_keys=False, default_flow_style=False)
                else:  # json
                    content = json.dumps(template_dict, indent=2)
                output_file = sheets_dir / f"{model_name.lower()}.{file_extension}"
                with open(output_file, 'w') as file:
                    file.write(content)
                logger.info(f"Generated {format.upper()} template for {model_name}")

        logger.info(f"{format.upper()} templates have been generated in {output_dir}")
        return single_output_file
    except Exception as e:
        logger.exception(f"An error occurred while generating {format.upper()} templates: {e}")
        raise

def generate_content(template_file: Path, user_prompt: str) -> Dict[str, Any]:
    """
    Generate content based on the template and user prompt using the local vLLM server.

    Args:
        template_file (Path): Path to the template file.
        user_prompt (str): User's input prompt for content generation.

    Returns:
        Dict[str, Any]: Generated content as a dictionary.

    Raises:
        Exception: If an error occurs during content generation.
    """
    with open(template_file, 'r') as f:
        template_content = f.read()

    system_prompt = f"""
    You are a creative worldbuilding assistant. Your task is to fill out the following template with rich, imaginative content based on the user's prompt. Ensure that the content is consistent and fits within the specified data structure. Here's the template:

    {template_content}

    Please fill out this template with creative content that matches the user's prompt. Maintain the structure of the template, replacing placeholder values with appropriate content. Ensure consistency throughout the generated world.
    """

    try:
        response = client.chat.completions.create(
            model=VLLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000  # Adjust as needed
        )

        generated_content = response.choices[0].message.content
        return json.loads(generated_content) if template_file.suffix == '.json' else yaml.safe_load(generated_content)
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        raise

def main():
    """
    Main function to parse arguments and generate templates or content.

    This function handles command-line arguments, generates templates based on the input file,
    and optionally generates content using the local vLLM server if a prompt is provided.
    """
    parser = argparse.ArgumentParser(description="Generate YAML or JSON templates and content from Python data models.")
    parser.add_argument("input_file", type=Path, help="Input Python file containing data models")
    parser.add_argument("--yaml", action="store_true", help="Generate YAML templates")
    parser.add_argument("--json", action="store_true", help="Generate JSON templates")
    parser.add_argument("--prompt", nargs="+", help="Prompt for content generation")

    args = parser.parse_args()

    output_dir = DEFAULT_OUTPUT_DIR

    if args.yaml or args.json:
        format = 'yaml' if args.yaml else 'json'
        template_file = generate_templates(args.input_file, output_dir, format)

        if args.prompt:
            prompt = " ".join(args.prompt)
            generated_content = generate_content(template_file, prompt)
            output_file = output_dir / f"generated_content.{format}"
            with open(output_file, 'w') as f:
                if format == 'yaml':
                    yaml.dump(generated_content, f, sort_keys=False, default_flow_style=False)
                else:
                    json.dump(generated_content, f, indent=2)
            logger.info(f"Generated content saved to: {output_file}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()