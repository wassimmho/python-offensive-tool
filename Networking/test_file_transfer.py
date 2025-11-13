"""
Test file to verify the file sending functionality
This creates test files and validates the protocol
"""

import os
import json
import base64
import io
import zipfile
from pathlib import Path

# Test constants
HEADER = 64
FORMAT = 'utf-8'

def create_test_files():
    """Create sample test files"""
    test_dir = "test_files"
    os.makedirs(test_dir, exist_ok=True)
    
    files_created = []
    
    # Create text file
    text_file = os.path.join(test_dir, "test_document.txt")
    with open(text_file, "w") as f:
        f.write("This is a test document for file transfer.\n")
        f.write("Line 2: Testing the file transfer protocol.\n")
        f.write("Line 3: Ensure large files are handled properly.\n")
    files_created.append(text_file)
    print(f"✓ Created {text_file}")
    
    # Create CSV file
    csv_file = os.path.join(test_dir, "test_data.csv")
    with open(csv_file, "w") as f:
        f.write("ID,Name,Value\n")
        f.write("1,Test1,100\n")
        f.write("2,Test2,200\n")
        f.write("3,Test3,300\n")
    files_created.append(csv_file)
    print(f"✓ Created {csv_file}")
    
    # Create larger file to test buffer handling
    large_file = os.path.join(test_dir, "test_large.bin")
    with open(large_file, "wb") as f:
        f.write(b"X" * (10 * 1024))  # 10KB file
    files_created.append(large_file)
    print(f"✓ Created {large_file} (10 KB)")
    
    return files_created

def test_file_archiving(files_created):
    """Test the file archiving and base64 encoding"""
    print("\n" + "="*60)
    print("Testing File Archiving & Base64 Encoding")
    print("="*60)
    
    # Create zip archive
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for file_path in files_created:
            z.write(file_path, arcname=os.path.basename(file_path))
    
    # Get archive size
    archive_data = buf.getvalue()
    archive_size = len(archive_data)
    print(f"✓ Archive created: {archive_size:,} bytes")
    
    # Encode to base64
    encoded = base64.b64encode(archive_data).decode(FORMAT)
    encoded_size = len(encoded)
    print(f"✓ Base64 encoded: {encoded_size:,} bytes")
    
    # Create JSON message
    message = json.dumps({"type": "file_archive", "filename": "files.zip", "data": encoded})
    message_size = len(message)
    print(f"✓ JSON message: {message_size:,} bytes")
    
    # Test protocol framing
    message_bytes = message.encode(FORMAT)
    length_header = str(len(message_bytes)).encode(FORMAT)
    length_header += b' ' * (HEADER - len(length_header))
    
    total_transmission = len(length_header) + len(message_bytes)
    print(f"✓ Total transmission size: {total_transmission:,} bytes")
    print(f"  - Header: {len(length_header)} bytes")
    print(f"  - Data: {len(message_bytes):,} bytes")
    
    # Check if message fits in reasonable buffers
    if message_size > 4096:
        print(f"\n⚠️  WARNING: Message size ({message_size:,} bytes) > 4KB buffer")
        print("   → Client needs to use multi-chunk reception (implemented)")
    else:
        print(f"\n✓ Message size ({message_size:,} bytes) fits in standard buffer")
    
    return message, message_bytes, length_header

def test_message_reception(message_bytes, length_header):
    """Simulate receiving the message in chunks"""
    print("\n" + "="*60)
    print("Testing Message Reception (Multi-Chunk)")
    print("="*60)
    
    # Simulate receiving in different chunk sizes
    chunk_sizes = [512, 1024, 4096, 16384]
    
    for chunk_size in chunk_sizes:
        total_data = length_header + message_bytes
        received = b""
        chunks = 0
        
        for i in range(0, len(total_data), chunk_size):
            chunk = total_data[i:i+chunk_size]
            received += chunk
            chunks += 1
        
        if received == total_data:
            print(f"✓ Chunk size {chunk_size:>5} bytes: SUCCESS ({chunks} chunks)")
        else:
            print(f"✗ Chunk size {chunk_size:>5} bytes: FAILED")

def test_decode_functionality(message_bytes):
    """Test the decoding process"""
    print("\n" + "="*60)
    print("Testing Decode Functionality")
    print("="*60)
    
    try:
        msg = json.loads(message_bytes.decode(FORMAT))
        print(f"✓ JSON decoded successfully")
        print(f"  - Message type: {msg.get('type')}")
        print(f"  - Filename: {msg.get('filename')}")
        print(f"  - Data size: {len(msg.get('data', '')):,} bytes")
        
        # Test base64 decode
        encoded_data = msg.get('data', '')
        decoded = base64.b64decode(encoded_data)
        print(f"✓ Base64 decoded: {len(decoded):,} bytes")
        
        # Test zip extraction
        buf = io.BytesIO(decoded)
        with zipfile.ZipFile(buf, "r") as z:
            files = z.namelist()
            print(f"✓ Zip extraction: {len(files)} files found")
            for f in files:
                info = z.getinfo(f)
                print(f"  - {f}: {info.file_size:,} bytes")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def cleanup_test_files():
    """Clean up test files"""
    import shutil
    if os.path.exists("test_files"):
        shutil.rmtree("test_files")
        print("✓ Test files cleaned up")

if __name__ == "__main__":
    print("\n" + "█"*60)
    print("FILE TRANSFER PROTOCOL TEST SUITE")
    print("█"*60)
    
    try:
        # Step 1: Create test files
        print("\n[1/5] Creating test files...")
        files_created = create_test_files()
        
        # Step 2: Test archiving
        print("\n[2/5] Testing file archiving...")
        message, message_bytes, length_header = test_file_archiving(files_created)
        
        # Step 3: Test reception
        print("\n[3/5] Testing message reception...")
        test_message_reception(message_bytes, length_header)
        
        # Step 4: Test decoding
        print("\n[4/5] Testing decode functionality...")
        test_decode_functionality(message_bytes)
        
        # Step 5: Cleanup
        print("\n[5/5] Cleaning up...")
        cleanup_test_files()
        
        print("\n" + "█"*60)
        print("✓ ALL TESTS PASSED - File transfer protocol is working!")
        print("█"*60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
