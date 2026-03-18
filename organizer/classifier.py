from pathlib import Path
from .config import FILE_CATEGORIES


def classify_file(file_path):
    ext = Path(file_path).suffix.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return "Others"


def classify_all(files):
    result = []
    for f in files:
        result.append({
            "path":          f,
            "name":          f.name,
            "extension":     f.suffix.lower(),
            "category":      classify_file(f),
            "size":          f.stat().st_size,
            "original_path": str(f.resolve()),
        })
    return result
