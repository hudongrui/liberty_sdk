# Liberty SDK

## Overview

`liberty_sdk` is a Python software develop kit for working with Synopsys Liberty standard.

## Liberty Format Reference
Reference: https://media.c3d2.de/mgoblin_media/media_entries/659/Liberty_User_Guides_and_Reference_Manual_Suite_Version_2017.06.pdf

## Features

- **Parser**: Parses Liberty files and converts them into a structured format.
- **JSON Serialization**: Converts parsed Liberty files into JSON format.
- **Liberty File Generation**: Generates Liberty files from the parsed data structure.
- **Compare Lib**: Compare cell/pin, measurement and project setup for LIB

## Project Structure

- `main.py`: The main script to run the parser and perform conversions.
- `parser/liberty_parser.py`: Contains the core parsing logic and data structures.
- `test/test_cell.lib`: Sample Liberty file used for testing.
- `test/test_cell.json`: JSON output generated from the sample Liberty file.
- `test/output_cell.lib`: Liberty file generated from the parsed data structure.

## Installation 

To install the SDK, use the following command:
```commandline
pip install
```

## Usage

### Setup

1. Clone the repository.
2. Install the required dependencies using `pip`.

```sh
pip install -r requirements.txt
```

### Running the Parser

To parse a Liberty file and convert it to JSON:

```sh
python main.py
```

This will read the Liberty file `test/test_cell.lib`, parse it, and generate the JSON output in `test/test_cell.json`. It will also generate a new Liberty file `test/output_cell.lib` from the parsed data.

### Logging

Logs are written to `parser.log` and provide detailed information about the parsing process.

## Testing

The project includes several assertions in `main.py` to verify the correctness of the parsing and conversion processes. These assertions check the parsed data against expected values.

## License

See the `LICENSE` file for details.