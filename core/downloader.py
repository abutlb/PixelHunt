# core/downloader.py

import csv
import json
import tempfile
import urllib.request
from pathlib import Path
from typing import Generator

import cv2
import numpy as np
import requests
from rich.console import Console

console = Console()

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"}


def _download_image(url: str) -> np.ndarray | None:
    """يحمل صورة من URL ويرجعها كـ numpy array."""
    try:
        resp = requests.get(url.strip(), timeout=15)
        resp.raise_for_status()
        arr = np.frombuffer(resp.content, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        console.print(f"[yellow]⚠️  فشل تحميل: {url}  →  {e}[/yellow]")
        return None


def load_urls_from_file(file_path: Path) -> list[str]:
    """
    يقرأ روابط من:
    - ملف .txt  → سطر لكل رابط
    - ملف .csv  → عمود اسمه 'url' أو 'image_url' أو العمود الأول
    - ملف .json → list من strings أو list من objects فيها 'url'
    """
    suffix = file_path.suffix.lower()
    urls   = []

    if suffix == ".txt":
        urls = [
            line.strip()
            for line in file_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and line.startswith("http")
        ]

    elif suffix == ".csv":
        with open(file_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # ابحث عن عمود الـ URL
            url_col = None
            for candidate in ("url", "image_url", "link", "image"):
                if candidate in (reader.fieldnames or []):
                    url_col = candidate
                    break
            for row in reader:
                val = row.get(url_col) or list(row.values())[0]
                if val and val.startswith("http"):
                    urls.append(val.strip())

    elif suffix == ".json":
        data = json.loads(file_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            for item in data:
                if isinstance(item, str) and item.startswith("http"):
                    urls.append(item)
                elif isinstance(item, dict):
                    for key in ("url", "image_url", "link", "image"):
                        if key in item:
                            urls.append(item[key])
                            break

    return urls


def images_from_urls(
    urls: list[str],
    tmp_dir: Path,
) -> Generator[tuple[str, Path], None, None]:
    """
    يحمل كل رابط، يحفظه مؤقتاً، ويرجع (url, path).
    """
    tmp_dir.mkdir(parents=True, exist_ok=True)

    for i, url in enumerate(urls, 1):
        console.print(f"  [cyan]⬇️  ({i}/{len(urls)})[/cyan]  {url[:70]}...")
        img = _download_image(url)
        if img is None:
            continue

        # اسم الملف من الـ URL أو رقم تسلسلي
        name = Path(url.split("?")[0]).name
        if not any(name.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
            name = f"image_{i:04d}.jpg"

        path = tmp_dir / name
        cv2.imwrite(str(path), img)
        yield url, path
