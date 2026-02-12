# Usage (through pip install)

1. install package with `pip install git+https://github.com/licsth/LeitblattSkript.git`
2. run `leitblatt <csv>`, e.g. `leitblatt data.csv`; use the file containing the participant data as provided by the university
3. to specify number of tasks, add `--numTasks <number>` option, e.g. `--numTasks 5` to generate sheets with 5 tasks, must be at least 3
4. to generate pdfs too, add `--pdf` option
5. to specify minimum number of sheets, add `--minSheets <number>` option, e.g. `--minSheets 3` to always generate at least 3 sheets
