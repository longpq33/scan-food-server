from __future__ import annotations
from pathlib import Path
from typing import Tuple
from PIL import Image, UnidentifiedImageError


def _is_image_file(path: Path) -> bool:
    return path.suffix.lower() in {".jpg", ".jpeg", ".png"}


def clean_dataset(dataset_root: str | Path) -> Tuple[int, int]:
    """
    Quét toàn bộ dataset (train/val) và xoá file ảnh lỗi mà PIL không mở được.
    Trả về: (deleted_count, scanned_count)
    """
    root = Path(dataset_root)
    deleted = 0
    scanned = 0
    for split in ("train", "val"):
        split_dir = root / split
        if not split_dir.exists():
            continue
        for cls_dir in split_dir.iterdir():
            if not cls_dir.is_dir():
                continue
            for img_path in cls_dir.iterdir():
                if not img_path.is_file() or not _is_image_file(img_path):
                    continue
                scanned += 1
                try:
                    with Image.open(img_path) as im:
                        im.verify()  # quick check
                except (UnidentifiedImageError, OSError):
                    try:
                        img_path.unlink(missing_ok=True)
                        deleted += 1
                    except Exception:
                        # Nếu không xoá được thì bỏ qua để không dừng toàn bộ quy trình
                        pass
    return deleted, scanned


