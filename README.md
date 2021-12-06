# excel-font: Use MS Excel to create pixel fonts
## What's here

A script to convert an Excel spreadsheet, formatted in
a certain way, to a font usable by PC/Macs.

One example spreadsheet is included to get you going.

Uses [fontParts](https://fontparts.robotools.dev/en/stable/) and [fontmake](https://github.com/googlefonts/fontmake).

# Why?

Good question, and one I fully intend to answer when I
actually have an answer.

- Python - tested on v3.9.
## Installation

The best way of running Python is to create a virtual environment. Open a terminal in this folder (`/python`)

```
python3 -m venv .
source ./bin/activate
pip3 install fontparts fontmake pandas openpyxl
```

## Usage

```
python src/convertExcelToFont.py -i <input_file> -o <output_file> -f <font_format>
```

Where `-f` can be any one of `ufo`, `ttf` or `otf`

## Sample font

Have a look in `sources` and feel free to try the script out!
