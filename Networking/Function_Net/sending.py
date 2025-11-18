import base64
import gzip
import os
import json
from pathlib import Path
from tkinter import Tk, filedialog


def files_to_base64(file_paths):
    if isinstance(file_paths, str):
        file_paths = [file_paths]
    
    result = {}
    for file_path in file_paths:
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
                encoded = base64.b64encode(file_data).decode('utf-8')
                result[os.path.basename(file_path)] = encoded
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    
    return result


def files_to_base64_archive(file_paths):
    if isinstance(file_paths, str):
        file_paths = [file_paths]
    
    result = {}
    for file_path in file_paths:
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()

                compressed_data = gzip.compress(file_data, compresslevel=9)
                
                encoded = base64.b64encode(compressed_data).decode('utf-8')
                result[os.path.basename(file_path)] = encoded
                
               
                original_size = len(file_data)
                compressed_size = len(compressed_data)
                ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
                
                print(f"[COMPRESS] {os.path.basename(file_path)}: {original_size} bytes -> {compressed_size} bytes ({ratio:.1f}% reduction)")
        
        except Exception as e:
            print(f"Error processing file ")
    
    return result


def base64_to_file(base64_string, output_path):
    try:
        file_data = base64.b64decode(base64_string)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(file_data)
        
        return True
    except Exception as e:
        print(f"Error writing file)")
        return False


def base64_archive_to_files(base64_string, output_dir):

    try:
        os.makedirs(output_dir, exist_ok=True)
        

        compressed_data = base64.b64decode(base64_string)
        
        decompressed_data = gzip.decompress(compressed_data)
        
        return decompressed_data
    
    except Exception as e:
        print(f"Error decompress ")
        return None


def selecting_files():

    try:
        root = Tk()
        root.withdraw()  
        
        files = filedialog.askopenfilenames(
            title="Select files to send",
            filetypes=[("All files", "*.*")]
        )
        
        return list(files)
    
    except Exception as e:
        print(f"Error selecting the files ")
        return []
