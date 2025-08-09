from __future__ import annotations
from pathlib import Path
from typing import Iterable
import time
import requests
from duckduckgo_search import DDGS


def _download(url: str, dest: Path, timeout: int = 20) -> bool:
    try:
        r = requests.get(url, timeout=timeout, stream=True)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception:
        return False


def crawl_images_for_class(dataset_dir: Path, class_name: str, num_images: int = 30, search_keywords: list[str] | None = None) -> None:
    """Tải ảnh cho một lớp vào dataset_dir/train/<class>/ và dataset_dir/val/<class>/.
    Hỗ trợ danh sách từ khoá tìm kiếm để nâng chất lượng kết quả.
    """
    train_dir = dataset_dir / "train" / class_name
    val_dir = dataset_dir / "val" / class_name
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)

    # Tạo tập kết quả bằng cách gộp nhiều truy vấn nếu cung cấp
    queries = search_keywords or [class_name]
    results: list[dict] = []
    with DDGS() as ddgs:
        for q in queries:
            for r in ddgs.images(keywords=q, max_results=num_images, safesearch="Off"):
                if "image" in r:
                    results.append(r)
                if len(results) >= num_images:
                    break
            if len(results) >= num_images:
                break

    # Chia 80/20 train/val
    split_idx = max(1, int(len(results) * 0.8))
    train_items = results[:split_idx]
    val_items = results[split_idx:]

    # Bắt đầu index theo số ảnh đã có để tránh ghi đè
    start_train_idx = len(list(train_dir.glob("*.jpg")))
    start_val_idx = len(list(val_dir.glob("*.jpg")))

    # Tải
    for i, item in enumerate(train_items, start=start_train_idx):
        url = item.get("image")
        if not url:
            continue
        ext = ".jpg"
        dest = train_dir / f"{class_name}_{i}{ext}"
        if _download(url, dest):
            time.sleep(0.1)

    for i, item in enumerate(val_items, start=start_val_idx):
        url = item.get("image")
        if not url:
            continue
        ext = ".jpg"
        dest = val_dir / f"{class_name}_{i}{ext}"
        if _download(url, dest):
            time.sleep(0.1)


def build_dataset(dataset_dir: str | Path, classes: Iterable[str], images_per_class: int = 30) -> str:
    ds_dir = Path(dataset_dir)
    ds_dir.mkdir(parents=True, exist_ok=True)
    # Map từ khoá tìm kiếm riêng cho một số lớp khó
    keyword_map: dict[str, list[str]] = {
        "bun_cha": [
            "bun cha",
            "bún chả",
            "bun cha ha noi",
            "bun cha vietnamese",
        ],
        "pho_bo": [
            "pho bo",
            "phở bò",
            "vietnamese beef noodle soup",
            "pho vietnamese beef",
        ],
        "vit_quay": [
            "vịt quay",
            "vit quay",
            "roast duck",
            "peking duck",
        ],
        "ga_quay": [
            "gà quay",
            "ga quay",
            "roast chicken",
            "rotisserie chicken",
        ],
        "muc_kho": [
            "mực khô",
            "muc kho",
            "dried squid",
            "grilled dried squid",
        ],
        "banh_my": [
            "bánh mì",
            "banh mi",
            "banh my",
            "vietnamese baguette",
            "vietnamese sandwich",
        ],
    }
    for cls in classes:
        crawl_images_for_class(
            ds_dir,
            cls,
            images_per_class,
            search_keywords=keyword_map.get(cls),
        )
    return str(ds_dir.resolve())


