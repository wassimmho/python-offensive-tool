import base64
import gzip
import os
from pathlib import Path


def receive_and_decompress_file(base64_string, filename, output_dir="logs/files"):
    result = {
        'success': False,
        'filename': filename,
        'path': None,
        'original_size': 0,
        'compressed_size': 0,
        'message': ''
    }
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        compressed_data = base64.b64decode(base64_string)
        result['compressed_size'] = len(compressed_data)
        
        decompressed_data = gzip.decompress(compressed_data)
        result['original_size'] = len(decompressed_data)
        
        output_path = os.path.join(output_dir, filename)
        
        output_dir_full = os.path.dirname(output_path)
        if output_dir_full:
            os.makedirs(output_dir_full, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(decompressed_data)
        
        result['success'] = True
        result['path'] = os.path.abspath(output_path)
        
        compression_ratio = (1 - result['compressed_size'] / result['original_size']) * 100 if result['original_size'] > 0 else 0
        
        result['message'] = f"✓ File received and decompressed: {filename} ({result['original_size']} bytes, {compression_ratio:.1f}% reduction)"
        
        print(f"[DECOMPRESS] {filename}: {result['compressed_size']} bytes -> {result['original_size']} bytes ({compression_ratio:.1f}% reduction)")
        print(f"[SAVED] {result['path']}")
        
        return result
    
    except Exception as e:
        result['message'] = f"✗ Error receiving file {filename}: {str(e)}"
        print(f"[ERROR] {result['message']}")
        return result


def receive_multiple_files(base64_dict, output_dir="logs/files"):

    results = []
    
    for filename, base64_string in base64_dict.items():
        result = receive_and_decompress_file(base64_string, filename, output_dir)
        results.append(result)
    
    return results


def receive_file_simple(base64_string, filename, output_dir="logs/files"):
   
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        file_data = base64.b64decode(base64_string)
        
        output_path = os.path.join(output_dir, filename)
        
        with open(output_path, 'wb') as f:
            f.write(file_data)
        
        print(f"[SAVED] {filename} to {os.path.abspath(output_path)}")
        return True
    
    except Exception as e:
        print(f"[ERROR] Error receiving file")
        return False
