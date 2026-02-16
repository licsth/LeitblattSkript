# Usage (through pip install)

1. install package with
```console
pip install git+https://github.com/licsth/LeitblattSkript.git
```
2. run `leitblatt <file>`, e.g. `leitblatt data.csv`; use the file containing the participant data as provided by the university. You can give multiple files, e.g. `leitblatt data1.csv data2.txt`, in which case the participants from all files will be combined into one set of sheets
3. to specify number of tasks, add `--numTasks <number>` option, e.g. `--numTasks 5` to generate sheets with 5 tasks, must be at least 3
4. to generate a PDF too, add `--pdf` option
5. to specify minimum number of sheets, add `--minSheets <number>` option, e.g. `--minSheets 3` to always generate at least 3 sheets
6. to sort participants alphabetically across all files, add `--sort` option; if not set, the order from the input file(s) is preserved
