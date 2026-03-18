import numpy as np
import pandas as pd

from .chart import generate_chart


def build_statistics(organized_files):
    df    = pd.DataFrame(organized_files)
    sizes = df["size"].to_numpy()

    category_counts = df["category"].value_counts().to_dict()

    category_sizes = {
        k: round(v / 1024, 2)
        for k, v in df.groupby("category")["size"].sum().items()
    }

    top5 = (
        df[["name", "category", "size"]]
        .sort_values("size", ascending=False)
        .head(5)
        .to_dict(orient="records")
    )

    file_list = (
        df[["name", "extension", "category", "size", "new_path"]]
        .to_dict(orient="records")
    )

    return {
        "total_files":        len(df),
        "total_size_mb":      round(df["size"].sum() / (1024 * 1024), 2),
        "category_counts":    category_counts,
        "category_sizes":     category_sizes,
        "largest_file_size":  round(float(np.max(sizes))    / 1024, 2),
        "smallest_file_size": round(float(np.min(sizes))    / 1024, 2),
        "average_file_size":  round(float(np.mean(sizes))   / 1024, 2),
        "median_file_size":   round(float(np.median(sizes)) / 1024, 2),
        "std_file_size":      round(float(np.std(sizes))    / 1024, 2),
        "top5_files":         top5,
        "file_list":          file_list,
        "chart_b64":          generate_chart(category_counts),
    }
