from __future__ import annotations
from pathlib import Path
from typing import Tuple
import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import mobilenet_v3_large, MobileNet_V3_Large_Weights

from ..config import MODEL_DIR, MODEL_PATH, LABELS_PATH, DEFAULT_IMAGE_SIZE


def _build_dataloaders(dataset_dir: str, batch_size: int) -> Tuple[DataLoader, DataLoader, int, list[str]]:
    dataset_dir = Path(dataset_dir)
    train_dir = dataset_dir / "train"
    val_dir = dataset_dir / "val"

    train_tf = transforms.Compose([
        transforms.RandomResizedCrop(DEFAULT_IMAGE_SIZE, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(0.2, 0.2, 0.2, 0.05),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    val_tf = transforms.Compose([
        transforms.Resize((DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    train_ds = datasets.ImageFolder(str(train_dir), transform=train_tf)
    val_ds = datasets.ImageFolder(str(val_dir), transform=val_tf)

    class_names = train_ds.classes
    num_classes = len(class_names)

    # Weighted sampling để cân bằng batch theo tần suất lớp
    from torch.utils.data import WeightedRandomSampler
    import numpy as np

    targets = [train_ds.samples[i][1] for i in range(len(train_ds))]
    class_counts = np.bincount(targets, minlength=num_classes)
    class_counts[class_counts == 0] = 1
    weights_per_class = 1.0 / class_counts
    sample_weights = [weights_per_class[t] for t in targets]
    sampler = WeightedRandomSampler(sample_weights, num_samples=len(sample_weights), replacement=True)

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        sampler=sampler,
        shuffle=False,
        num_workers=2,
        pin_memory=True,
    )
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=True)

    return train_loader, val_loader, num_classes, class_names


def train_model(dataset_dir: str, num_epochs: int = 5, batch_size: int = 32, learning_rate: float = 5e-4) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    train_loader, val_loader, num_classes, class_names = _build_dataloaders(dataset_dir, batch_size)

    model = mobilenet_v3_large(weights=MobileNet_V3_Large_Weights.DEFAULT)
    # Fine-tune sâu hơn: mở một số block cuối
    for i, (name, param) in enumerate(model.named_parameters()):
        param.requires_grad = False
    # mở khóa phần classifier và layer conv cuối
    for param in model.classifier.parameters():
        param.requires_grad = True
    # optional: bật grad cho phần cuối của features (last 2 inverted residual blocks)
    for layer in list(model.features.children())[-4:]:
        for p in layer.parameters():
            p.requires_grad = True

    num_features = model.classifier[3].in_features
    model.classifier[3] = torch.nn.Linear(num_features, num_classes)
    model = model.to(device)

    # Class weighting để giúp các lớp khó
    # Đếm số ảnh mỗi lớp (hỗ trợ .jpg/.jpeg/.png)
    class_counts = []
    for c in class_names:
        cls_dir = Path(dataset_dir) / 'train' / c
        num_jpg = sum(1 for _ in cls_dir.glob('*.jpg'))
        num_jpeg = sum(1 for _ in cls_dir.glob('*.jpeg'))
        num_png = sum(1 for _ in cls_dir.glob('*.png'))
        class_counts.append(num_jpg + num_jpeg + num_png)
    total = sum(class_counts)
    weights = [total / max(1, c) for c in class_counts]
    norm = sum(weights)
    weights = [w / norm for w in weights]
    criterion = torch.nn.CrossEntropyLoss(weight=torch.tensor(weights, dtype=torch.float32).to(device))
    optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=learning_rate)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max(1, num_epochs))

    best_acc = 0.0
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        running_corrects = 0
        total = 0
        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad(set_to_none=True)
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            preds = outputs.argmax(dim=1)
            running_corrects += (preds == labels).sum().item()
            total += images.size(0)

        train_loss = running_loss / total if total > 0 else 0.0
        train_acc = running_corrects / total if total > 0 else 0.0

        # validate
        model.eval()
        val_corrects = 0
        val_total = 0
        with torch.inference_mode():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)
                outputs = model(images)
                preds = outputs.argmax(dim=1)
                val_corrects += (preds == labels).sum().item()
                val_total += images.size(0)
        val_acc = val_corrects / val_total if val_total > 0 else 0.0

        print(f"Epoch {epoch+1}/{num_epochs} - train_loss={train_loss:.4f} train_acc={train_acc:.4f} val_acc={val_acc:.4f}")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), MODEL_PATH)
            Path(LABELS_PATH).write_text("\n".join(class_names), encoding="utf-8")
            print(f"Saved best model to {MODEL_PATH} with val_acc={best_acc:.4f}")

        scheduler.step()

    print("Training finished. Best val_acc=", best_acc)
