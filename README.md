# Loreweaver README

## Overview

Loreweaver is a powerful toolset for dynamic worldbuilding, narrative creation, and game master assistance. It provides a flexible, scalable framework for creating rich, interconnected universes with deep lore and complex character interactions.

## Project Structure

```
loreweaver/
├── src/
│   ├── lore/
│   │   └── core.py
│   ├── weave.py
│   ├── character_development_kit/
│   ├── event_development_kit/
│   ├── narrative_development_kit/
│   ├── world_development_kit/
│   ├── universe_development_kit/
│   └── simulation_development_kit/
└── requirements.txt
```

## Key Components

1.  **core.py**: Contains foundational data models for worldbuilding elements (characters, items, locations, events, etc.).
2.  **weave.py**: YAML template generator for creating structured data files from Python models.
3.  **Development Kits**: Specialized tools for different aspects of worldbuilding and storytelling.

## Installation

1.  Clone the repository:

    Copy

    `git clone https://github.com/your-username/loreweaver.git cd loreweaver`

2.  Install dependencies:

    Copy

    `pip install -r requirements.txt`


## Usage

### Generating YAML Templates

Use `weave.py` to generate YAML templates from your data models:

Copy

`python src/weave.py src/lore/core.py --output-type sheets --process-type full --output ./templates`

Options:

-   `--output-type`: Choose between `sheets` (multiple files) or `single` (one file)
-   `--process-type`: Select `full` (includes descriptions) or `basic` (omits descriptions)
-   `--output`: Specify the output directory (default: ./yaml_templates)

### Development Kits

Each kit in the `src/` directory provides specialized tools for different aspects of worldbuilding:

-   **Character Development Kit**: Tools for creating and managing complex characters.
-   **Event Development Kit**: Utilities for crafting and linking significant events.
-   **Narrative Development Kit**: Aids for storyline creation and management.
-   **World Development Kit**: Tools for designing and evolving detailed worlds.
-   **Universe Development Kit**: Utilities for managing multiple worlds and dimensions.
-   **Simulation Development Kit**: Tools for running dynamic world simulations.

## Key Features

-   **Modular Design**: Easily extensible for custom worldbuilding needs.
-   **Version Control**: Built-in versioning for tracking changes in your world elements.
-   **Localization Support**: Multi-language support for global storytelling.
-   **Dynamic Relationships**: Model complex interactions between characters, factions, and more.
-   **Timeline Management**: Tools for managing branching and parallel timelines.
-   **Simulation Capabilities**: Run dynamic world simulations to evolve your universe.

## For Developers

-   The project uses Pydantic for data validation and serialization.
-   YAML is used for human-readable data storage and exchange.
-   Consider contributing to expand the capabilities of different development kits.

## For Worldbuilders

-   Utilize the various development kits to create rich, interconnected elements of your world.
-   Use the YAML templates to organize and visualize your world data.
-   Leverage the simulation capabilities to see how your world evolves over time.

## For Game Masters

-   Use the character and event development kits to create engaging NPCs and plot points.
-   Employ the simulation development kit to generate dynamic scenarios and world states.
-   Utilize the narrative development kit to manage complex, branching storylines.

## Requirements

-   Python 3.7+
-   pyyaml==6.0.2
-   pydantic==2.9.0
-   openai==1.44.0
-   vllm==0.6.0 (optional)

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on the GitHub repository or contact the maintainers directly.