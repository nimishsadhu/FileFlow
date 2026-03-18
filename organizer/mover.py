import json
import shutil
from pathlib import Path

UNDO_LOG = Path("reports/undo_log.json")


def move_files(classified_files, base_folder):
    
    """
    base/photo.jpg          → base/Images/photo.jpg
    base/my_photos/img.jpg  → base/my_photos/Images/img.jpg
    base/work/report.pdf    → base/work/Documents/report.pdf
    """
    
    results = []

    for f in classified_files:
        # Category folder lives next to the file, not always at base root
        dest_dir = f["path"].parent / f["category"]
        dest_dir.mkdir(exist_ok=True)

        dest = dest_dir / f["name"]

        # Collision-safe rename: photo.jpg → photo_1.jpg etc.
        if dest.exists():
            stem, suffix = Path(f["name"]).stem, Path(f["name"]).suffix
            counter = 1
            while dest.exists():
                dest = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1

        shutil.move(str(f["path"]), str(dest))
        f["new_path"] = str(dest.resolve())
        results.append(f)

    _save_undo_log(results)
    return results


def _save_undo_log(organized_files):
    """Persist a move log so undo_last_run() can reverse every move."""
    UNDO_LOG.parent.mkdir(exist_ok=True)
    log = [
        {
            "name":          f["name"],
            "original_path": f["original_path"],
            "new_path":      f["new_path"],
        }
        for f in organized_files
    ]
    with open(UNDO_LOG, "w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=2)


def undo_last_run():
    """Move every file back to its original location."""
    if not UNDO_LOG.exists():
        return {"success": False, "error": "No undo log found. Nothing to undo."}

    with open(UNDO_LOG, encoding="utf-8") as fh:
        log = json.load(fh)

    if not log:
        return {"success": False, "error": "Undo log is empty. Nothing to undo."}

    restored, failed = [], []

    for entry in log:
        src = Path(entry["new_path"])
        dst = Path(entry["original_path"])
        try:
            if not src.exists():
                failed.append(entry["name"])
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            restored.append(entry["name"])
        except Exception as e:
            failed.append(f"{entry['name']} ({e})")

    # Clear log so undo cannot be triggered twice on the same run
    UNDO_LOG.unlink(missing_ok=True)

    return {
        "success":      True,
        "restored":     len(restored),
        "failed":       len(failed),
        "failed_files": failed,
    }
