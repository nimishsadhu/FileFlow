from pathlib import Path

CATEGORY_NAMES = {
    "Images", "Videos", "Documents",
    "Audio", "Code", "Archives", "Others",
}


def scan_directory(folder_path, include_subfolders=False):
    target = Path(folder_path)

    if not target.exists():
        raise FileNotFoundError(f"Path does not exist: {folder_path}")
    if not target.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder_path}")

    if include_subfolders:
        files = []
        for item in target.rglob("*"):
            if not item.is_file():
                continue
            # Skip files already sitting inside one of our category folders
            # so re-running on an already-organised folder does nothing extra
            if item.parent.name in CATEGORY_NAMES:
                continue
            files.append(item)
        return files

    # Default: top-level files only
    return [item for item in target.iterdir() if item.is_file()]
