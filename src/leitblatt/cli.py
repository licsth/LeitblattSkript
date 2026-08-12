import csv
import argparse
import os
import math
import shutil
from odf.opendocument import load
from odf.table import Table, TableRow, TableColumn, TableCell
from odf.text import P
import subprocess


# ----------------------------
# Argumente
# ----------------------------

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("csvfiles", help="File path(s) to participant data", nargs="+")
    parser.add_argument("--numTasks", type=int, default=0, help="Number of tasks, >= 3")
    parser.add_argument("--minSheets", type=int, default=0, help="Generate at least this many sheets, even if not necessary based on participant count")
    parser.add_argument("--offset", type=int, default=0, help="Start the numbering of participants at this number. The numbering of sheets will start accordingly.")
    parser.add_argument("--sort", action="store_true", help="Sort participants alphabetically across all files")
    parser.add_argument("--pdf", action="store_true",
                        help="Generate PDF file with all sheets (requires LibreOffice in PATH)")
    return parser.parse_args()

def load_template():
    template_path = os.path.join(os.path.dirname(__file__), "data", "template.ods")
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")
    return template_path

# ----------------------------
# CSV einlesen (wie vorher)
# ----------------------------

def read_and_prepare_data(filenames, sort, offset=0):
    rows = []
    for filename in filenames:
        with open(filename, "r", encoding="iso-8859-1", newline="") as f:
            # Sample lesen für Delimiter-Erkennung
            sample = f.read(4096)
            f.seek(0)

            dialect = csv.Sniffer().sniff(sample, delimiters=";\t")

            reader = csv.reader(f, dialect)

            # Erste Zeile = Meta-Zeile
            meta_row = next(reader)
            klausurname = meta_row[1].strip() if len(meta_row) > 1 else ""

            # Zweite Zeile = Header
            header = next(reader)

            # Restliche Zeilen mit DictReader lesen
            dict_reader = csv.DictReader(f, fieldnames=header, dialect=dialect)
            rows.extend(list(dict_reader))

    prepared = []
    one_has_number = False
    for row in rows:
        vorname = (row.get("Vorname") or "").strip()
        mittelname = (row.get("Mittelname") or "").strip()
        full_vorname = f"{vorname} {mittelname}".strip()
        if row.get("Prüfungsnummer", "").strip():
            one_has_number = True
        
        prepared.append({
            "Name": row["Name"].strip(),
            "Vorname": full_vorname,
            "Matrikelnummer": row["Matrikelnummer"].strip(),
            "Nummer": int(row.get("Prüfungsnummer", "").strip()) + offset if row.get("Prüfungsnummer", "").strip() else None
        })

    if sort:
        prepared.sort(key=lambda x: (x["Name"].lower(), x["Vorname"].lower()))

    if sort or not one_has_number:
        for i, row in enumerate(prepared, start=1+offset):
            row["Nummer"] = i

    return prepared, klausurname




# ----------------------------
# Aufteilen
# ----------------------------

def split_into_chunks(data, min_sheets, max_per_sheet=20):
    total = len(data)

    if total <= min_sheets * max_per_sheet:
        sheets = min_sheets
    else:
        sheets = math.ceil(total / max_per_sheet)

    chunk_size = math.ceil(total / sheets)

    return [
        data[i * chunk_size:(i + 1) * chunk_size]
        for i in range(sheets)
    ]


# ----------------------------
# ODS beschreiben
# ----------------------------

def write_to_ods(template_path, output_path, students, klausurname, num_tasks, sheet_number):
    shutil.copy(template_path, output_path)

    doc = load(output_path)
    sheet = doc.spreadsheet.getElementsByType(Table)[0]
    # reset name of the sheet
    sheet.setAttribute("name", f"Sheet{sheet_number}")
    rows = sheet.getElementsByType(TableRow)

    

    # -------------------------------------
    # 1️⃣ Titel in A1 setzen
    # -------------------------------------
    first_row = rows[0]
    first_row_cells = first_row.getElementsByType(TableCell)

    set_cell(first_row_cells[0], f"Ergebnisse der Klausur {klausurname}")

    # Sheet-Nummer in letzte Spalte von Zeile 1
    last_cell = first_row_cells[-2]
    set_cell(last_cell, f"{sheet_number}")

    start_row_index = 3  # Zeile 4 (0-basiert)
    num_duplications = num_tasks - 3

    for i in range(num_duplications):
        new_column = TableColumn()
        template_column = sheet.getElementsByType(TableColumn)[4]
        new_column.setAttribute("stylename", template_column.getAttribute("stylename"))
        sheet.insertBefore(new_column, template_column)  # Am Ende der Spalten einfügen
        for row in rows:
            cells = row.getElementsByType(TableCell)
            dupulcation_index = 5 if len(cells) >= 6 else 1
            if len(cells) < dupulcation_index + 1:
                continue  # Nicht genug Zellen, überspringen
            copy_cell = cells[dupulcation_index]
            new_cell = TableCell()
            new_cell.setAttribute("stylename", copy_cell.getAttribute("stylename"))
            row.insertBefore(new_cell, copy_cell)
    
    header_row = rows[start_row_index - 1]
    header_cells = header_row.getElementsByType(TableCell)
    for excercise in range(num_duplications+2):
        set_cell(header_cells[excercise+5], f"{excercise + 2}.")

    for i, student in enumerate(students):
        row = rows[start_row_index + i]
        cells = row.getElementsByType(TableCell)

        # A-D setzen
        set_cell(cells[0], str(student["Nummer"]))
        set_cell(cells[1], student["Name"])
        set_cell(cells[2], student["Vorname"])
        set_cell(cells[3], student["Matrikelnummer"])

    doc.save(output_path)


def set_cell(cell, value):
    # Alten Inhalt löschen
    for child in list(cell.childNodes):
        cell.removeChild(child)

    cell.addElement(P(text=value))

def convert_to_pdf(path):
    # Liste der möglichen Pfade zu soffice
    possible_paths = [
        "soffice",  # Standard: im PATH
        "/Applications/LibreOffice.app/Contents/MacOS/soffice"  # macOS Standard
    ]

    for lo_path in possible_paths:
        try:
            subprocess.run(
                [
                    lo_path,
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", os.path.dirname(path),
                    path,
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # Erfolgreich → Funktion beenden
            return
        except FileNotFoundError:
            continue  # Nächster Pfad
        except subprocess.CalledProcessError:
            print(f"PDF conversion failed for {path}")
            return

    # Wenn keiner der Pfade funktioniert hat
    print("LibreOffice (soffice) not found. Please install it or add it to your PATH.")


def combine_ods(ods_files, output_path):
    if not ods_files:
        print("No ODS files to combine.")
        return

    # Lade das erste Dokument als Basis
    base_doc = load(ods_files[0])
    # base_sheet = base_doc.spreadsheet.getElementsByType(Table)[0]

    for ods_file in ods_files[1:]:
        doc = load(ods_file)
        sheet = doc.spreadsheet.getElementsByType(Table)[0]
        base_doc.spreadsheet.addElement(sheet)
        
    base_doc.save(output_path)

# ----------------------------
# Main
# ----------------------------

def main():
    args = parse_args()
    
    filenames = args.csvfiles

    base_name = os.path.splitext(os.path.basename(filenames[0]))[0]
    out_dir = os.path.dirname(filenames[0])

    data, klausurname = read_and_prepare_data(filenames, sort=args.sort, offset=args.offset)
    chunks = split_into_chunks(data, args.minSheets)

    out_ods_paths = []

    for i, chunk in enumerate(chunks, start=1):
        out_ods_path = os.path.join(out_dir, f"{base_name}_sheet_{i + args.offset//20 + (1 if args.offset != 0 else 0)}.ods")
        out_ods_paths.append(out_ods_path)
        write_to_ods(
            load_template(),
            out_ods_path,
            chunk,
            klausurname,
            args.numTasks,
            i+args.offset//20 + (1 if args.offset != 0 else 0),
        )
        
    combined_out_ods_path = os.path.join(out_dir, f"{base_name}_Leitblätter.ods")
    combine_ods(
        out_ods_paths,
        combined_out_ods_path
    )
    
    # delete out_ods_paths
    for path in out_ods_paths:
        os.remove(path)
    
    if args.pdf:
      out_pdf_path = os.path.join(out_dir, f"{base_name}_Leitblätter.pdf")
      convert_to_pdf(combined_out_ods_path)
      # Die PDF wird automatisch im gleichen Ordner wie das .ods erzeugt
      generated_pdf = os.path.splitext(combined_out_ods_path)[0] + ".pdf"
      if os.path.exists(generated_pdf):
          shutil.move(generated_pdf, out_pdf_path)


if __name__ == "__main__":
    main()
