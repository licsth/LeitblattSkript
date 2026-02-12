# Usage (through cloning the project and running the CLI)

0. clone project
1. run `python3 cli.py <csv>`, for me, `/usr/local/bin/python3.9`
2. to generate pdfs too, add `--pdf` option
3. to specify minimum number of sheets, add `--minSheets <number>` option, e.g. `--minSheets 3` to always generate at least 3 sheets

# Usage (through pip install)

1. install package with `pip install .` in the project directory
2. run `leitblatt <csv>`, e.g. `leitblatt data.csv`
3. add `--pdf` and `--minSheets` options as needed
