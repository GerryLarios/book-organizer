# Book Organizer

A CLI tool to organize eBook files (`.epub`, `.pdf`) into a clean folder structure compatible with [Jellyfin](https://jellyfin.org/).

## Output Structure

```
<directory>/
└── Author Name/
    └── Book Title/
        └── Book Title (Year).epub
```

- If the book has no author, it is placed under an `Unknown/` folder.
- If the year is not found in the metadata, it is omitted from the filename.

## Requirements

- Python 3.x
- [ebooklib](https://pypi.org/project/EbookLib/)
- [PyPDF2](https://pypi.org/project/PyPDF2/)

Install dependencies:

```bash
pip install ebooklib PyPDF2
```

## Usage

```bash
python main.py <directory>
```

### Example

```bash
python main.py ~/Books
```

This will scan `~/Books` for `.epub` and `.pdf` files and reorganize them in place.
