import argparse
import os
import re
import unicodedata

from ebooklib import epub  # type: ignore
from PyPDF2 import PdfReader  # type: ignore

UNKNOWN_AUTHOR = "Unknown"


def _first_author(raw):
    """Return only the first author from a potentially multi-author string."""
    if not raw:
        return None
    return re.split(r'\s*[&,;]\s*', raw.strip())[0].strip() or None


def get_pdf_metadata(file_path):
    try:
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            info = reader.metadata
            title = info.title.strip() if info.title else os.path.splitext(os.path.basename(file_path))[0]
            author = _first_author(info.author)
            year = _extract_year(info.get("/CreationDate", "") or "")
            return title, author, year
    except Exception as e:
        print(f"Warning: could not read PDF metadata for '{file_path}': {e}")
        return os.path.splitext(os.path.basename(file_path))[0], None, None


def get_epub_metadata(file_path):
    try:
        book = epub.read_epub(file_path)
        title_meta = book.get_metadata('DC', 'title')
        author_meta = book.get_metadata('DC', 'creator')
        date_meta = book.get_metadata('DC', 'date')
        title = title_meta[0][0].strip() if title_meta else os.path.splitext(os.path.basename(file_path))[0]
        author = _first_author(author_meta[0][0] if author_meta else None)
        year = _extract_year(date_meta[0][0] if date_meta else "")
        return title, author, year
    except Exception as e:
        print(f"Warning: could not read EPUB metadata for '{file_path}': {e}")
        return os.path.splitext(os.path.basename(file_path))[0], None, None


def _extract_year(value):
    match = re.search(r'\b(1[0-9]{3}|2[0-9]{3})\b', str(value))
    return match.group(1) if match else None


def sanitize(name):
    normalized = unicodedata.normalize("NFD", name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r'[\\/*?:"<>|]', "", ascii_name).strip()


def organize_files(directory):
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and not f.startswith('.')]
    except FileNotFoundError:
        print(f"Directory '{directory}' does not exist.")
        return
    except PermissionError:
        print(f"Permission denied to access '{directory}'.")
        return

    for file in files:
        file_path = os.path.join(directory, file)
        ext = os.path.splitext(file)[1].lower()

        if ext == '.pdf':
            title, author, year = get_pdf_metadata(file_path)
        elif ext == '.epub':
            title, author, year = get_epub_metadata(file_path)
        else:
            continue

        author_dir = sanitize(author) if author else UNKNOWN_AUTHOR
        title_clean = sanitize(title)
        book_name = f"{title_clean} ({year})" if year else title_clean

        dest_dir = os.path.join(directory, author_dir, title_clean)
        os.makedirs(dest_dir, exist_ok=True)

        dest_path = _unique_path(dest_dir, book_name, ext)
        os.rename(file_path, dest_path)
        print(f"Moved '{file}' → '{os.path.relpath(dest_path, directory)}'")


def _unique_path(directory, base_name, ext):
    dest = os.path.join(directory, f"{base_name}{ext}")
    counter = 1
    while os.path.exists(dest):
        dest = os.path.join(directory, f"{base_name} ({counter}){ext}")
        counter += 1
    return dest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize books into Author/Title/Title (Year) structure.")
    parser.add_argument("directory", type=str, help="Directory containing book files")
    args = parser.parse_args()

    organize_files(args.directory)