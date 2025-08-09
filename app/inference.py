from __future__ import annotations
from pathlib import Path
from typing import List, Tuple
import torch
from PIL import Image
from torchvision import transforms

from .config import MODEL_PATH, LABELS_PATH, DEFAULT_IMAGE_SIZE

_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_model = None
_labels: List[str] = []


def _load_labels(labels_path: Path) -> List[str]:
    if not labels_path.exists():
        return []
    return [line.strip() for line in labels_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_model() -> None:
    global _model, _labels
    _labels = _load_labels(LABELS_PATH)
    if not MODEL_PATH.exists():
        _model = None
        return
    # Kiến trúc cần khớp với script train (MobileNetV3 Small)
    from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights

    model = mobilenet_v3_small(weights=MobileNet_V3_Small_Weights.DEFAULT)
    num_features = model.classifier[3].in_features
    model.classifier[3] = torch.nn.Linear(num_features, len(_labels) if _labels else 1000)

    state = torch.load(MODEL_PATH, map_location="cpu")
    model.load_state_dict(state)
    model.eval().to(_device)
    _model = model


def ensure_loaded() -> None:
    if _model is None:
        load_model()


def _build_transform() -> transforms.Compose:
    return transforms.Compose([
        transforms.Resize((DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def predict(img: Image.Image) -> Tuple[str, float]:
    ensure_loaded()
    if _model is None:
        raise RuntimeError("Model chưa sẵn sàng. Hãy train trước hoặc đặt file models/best.pt và labels.txt")
    if not _labels:
        raise RuntimeError("Thiếu labels.txt. Hãy train để sinh labels")

    transform = _build_transform()
    tensor = transform(img).unsqueeze(0).to(_device)
    with torch.inference_mode():
        logits = _model(tensor)
        probs = torch.softmax(logits, dim=1)
        score, idx = torch.max(probs, dim=1)
        dish = _labels[int(idx.item())] if int(idx.item()) < len(_labels) else str(int(idx.item()))
        return dish, float(score.item())
