import argparse
import os
import re
from collections import defaultdict

from ebooklib import epub  # type: ignore
from PyPDF2 import PdfReader  # type: ignore


def get_pdf_title(file_path):
    try:
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            info = reader.metadata
            title = info.title if info.title else os.path.basename(file_path)
            author = info.author if info.author else "Unknown Author"
            return title.strip(), author.strip()
    except Exception as e:
        return f"Error reading PDF metadata: {e}", "Unknown Author"

def get_epub_title(file_path):
    try:
        book = epub.read_epub(file_path)
        title = book.get_metadata('DC', 'title')
        author = book.get_metadata('DC', 'creator')
        title = title[0][0].strip() if title else os.path.basename(file_path).strip()
        author = author[0][0].strip() if author else "Unknown Author"
        return title, author
    except Exception as e:
        return f"Error reading EPUB metadata: {e}", "Unknown Author"

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def get_unique_filename(directory, author, title, ext):
    base_name = f"{author} - {title}"
    counter = 1
    new_file_name = f"{base_name}{ext}"
    new_file_path = os.path.join(directory, new_file_name)
    while os.path.exists(new_file_path):
        new_file_name = f"{base_name} ({counter}){ext}"
        new_file_path = os.path.join(directory, new_file_name)
        counter += 1
    return new_file_path

def list_files(directory):
    try:
        # List all files in the given directory
        files = os.listdir(directory)
        files_by_extension = defaultdict(list)
        
        for file in files:
            file_path = os.path.join(directory, file)
            if os.path.isdir(file_path):
                continue  # Skip directories
            ext = os.path.splitext(file)[1]
            files_by_extension[ext].append(file)
        
        for ext, files in files_by_extension.items():
            ext_dir = os.path.join(directory, ext.lstrip('.'))
            os.makedirs(ext_dir, exist_ok=True)
            for file in files:
                file_path = os.path.join(directory, file)
                if ext == '.pdf':
                    title, author = get_pdf_title(file_path)
                    sanitized_title = sanitize_filename(title)
                    sanitized_author = sanitize_filename(author)
                    new_file_path = get_unique_filename(ext_dir, sanitized_author, sanitized_title, ext)
                elif ext == '.epub':
                    title, author = get_epub_title(file_path)
                    sanitized_title = sanitize_filename(title)
                    sanitized_author = sanitize_filename(author)
                    new_file_path = get_unique_filename(ext_dir, sanitized_author, sanitized_title, ext)
                else:
                    new_file_path = os.path.join(ext_dir, file)
                
                os.rename(file_path, new_file_path)
                print(f"Moved '{file}' to '{new_file_path}'")
    except FileNotFoundError:
        print(f"The directory {directory} does not exist.")
    except PermissionError:
        print(f"Permission denied to access {directory}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List files in a directory.")
    parser.add_argument("directory", type=str, help="The directory path")
    args = parser.parse_args()
    
    list_files(args.directory)