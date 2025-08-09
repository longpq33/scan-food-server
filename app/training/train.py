from __future__ import annotations
from pathlib import Path
from typing import Tuple
import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights

from ..config import MODEL_DIR, MODEL_PATH, LABELS_PATH, DEFAULT_IMAGE_SIZE


def _build_dataloaders(dataset_dir: str, batch_size: int) -> Tuple[DataLoader, DataLoader, int, list[str]]:
    dataset_dir = Path(dataset_dir)
    train_dir = dataset_dir / "train"
    val_dir = dataset_dir / "val"

    train_tf = transforms.Compose([
        transforms.Resize((DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(),
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

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=2, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=True)

    return train_loader, val_loader, num_classes, class_names


def train_model(dataset_dir: str, num_epochs: int = 5, batch_size: int = 32, learning_rate: float = 5e-4) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    train_loader, val_loader, num_classes, class_names = _build_dataloaders(dataset_dir, batch_size)

    model = mobilenet_v3_small(weights=MobileNet_V3_Small_Weights.DEFAULT)
    for param in model.features.parameters():
        param.requires_grad = False
    num_features = model.classifier[3].in_features
    model.classifier[3] = torch.nn.Linear(num_features, num_classes)
    model = model.to(device)

    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

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

        train_loss = running_loss / total
        train_acc = running_corrects / total

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

    print("Training finished. Best val_acc=", best_acc)
