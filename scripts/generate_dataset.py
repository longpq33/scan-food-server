from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

CLASSES = ["pho_bo", "bun_cha", "goi_cuon"]
ROOT = Path(__file__).resolve().parents[1] / "datasets" / "vn_food"
IMG_SIZE = (512, 512)


def ensure_dirs():
    for split in ["train", "val"]:
        for cls in CLASSES:
            (ROOT / split / cls).mkdir(parents=True, exist_ok=True)


def random_color(seed: int) -> tuple[int, int, int]:
    random.seed(seed)
    return tuple(random.randint(50, 200) for _ in range(3))


def draw_sample(text: str, seed: int) -> Image.Image:
    img = Image.new("RGB", IMG_SIZE, random_color(seed))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Arial.ttf", 48)
    except Exception:
        font = ImageFont.load_default()
    W, H = IMG_SIZE
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((W - w) / 2, (H - h) / 2), text, fill=(255, 255, 255), font=font)
    # thêm vài hình khối để khác nhau nhẹ
    for _ in range(5):
        x0 = random.randint(0, max(0, W - 50))
        y0 = random.randint(0, max(0, H - 50))
        x1 = min(W, x0 + random.randint(20, 120))
        y1 = min(H, y0 + random.randint(20, 120))
        draw.rectangle([x0, y0, x1, y1], outline=(255, 255, 255))
    return img


def main():
    ensure_dirs()
    for cls in CLASSES:
        # 5 ảnh/món: 4 train, 1 val
        for i in range(1, 6):
            split = "val" if i == 5 else "train"
            path = ROOT / split / cls / f"{cls}_{i}.jpg"
            img = draw_sample(f"{cls} #{i}", seed=hash((cls, i)) % (2**32))
            img.save(path, quality=90)
    print(f"Dataset created at: {ROOT}")


if __name__ == "__main__":
    main()
