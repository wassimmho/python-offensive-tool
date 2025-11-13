import tkinter as tk
from tkinter import filedialog
import base64
import gzip
import io
import zipfile
import os

def selecting_files():

    root = tk.Tk()
    root.withdraw() 

    file_paths = filedialog.askopenfilenames(title="Select Files")
    return list(file_paths)


# create a def turning files into base64 

def files_to_base64(file_paths, compresslevel=9):
    base64_files = {}
    for file_path in file_paths:
        with open(file_path, "rb") as file:
            data = file.read()
        compressed = gzip.compress(data, compresslevel)
        encoded_string = base64.b64encode(compressed).decode("utf-8")
        base64_files[file_path] = encoded_string
    return base64_files


def base64_to_file(encoded_string, output_path, decompress=True):
    raw = base64.b64decode(encoded_string)
    if decompress:
        try:
            raw = gzip.decompress(raw)
        except OSError:
            pass
    with open(output_path, "wb") as file:
        file.write(raw)


def files_to_base64_archive(file_paths, archive_name="files.zip"):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for file_path in file_paths:
            z.write(file_path, arcname=os.path.basename(file_path))
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    return {archive_name: encoded}


def base64_archive_to_files(encoded_string, output_dir):
    raw = base64.b64decode(encoded_string)
    buf = io.BytesIO(raw)
    with zipfile.ZipFile(buf, "r") as z:
        z.extractall(output_dir)



if __name__ == "__main__":
    selected_files = selecting_files()
    if selected_files:
        base64_encoded_files = files_to_base64(selected_files)
        for path, encoded in base64_encoded_files.items():
            print(f"File: {path}\nBase64 Encoded:\n{encoded}\n")
    else:
        print("No files selected.")
