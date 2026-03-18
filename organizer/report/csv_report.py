import pandas as pd
from pathlib import Path
from ..config import REPORTS_DIR, REPORT_FILENAME


def generate_report(organized_files):
    reports_dir = Path(REPORTS_DIR)
    reports_dir.mkdir(exist_ok=True)

    report_path = reports_dir / REPORT_FILENAME

    df = pd.DataFrame(organized_files)

    export = df[["name", "extension", "category", "size", "original_path", "new_path"]].copy()
    export = export.rename(columns={
        "name":          "File Name",
        "extension":     "Extension",
        "category":      "Category",
        "size":          "Size (bytes)",
        "original_path": "Original Path",
        "new_path":      "New Path",
    })

    export.to_csv(report_path, index=False, encoding="utf-8")
    return str(report_path.resolve())
