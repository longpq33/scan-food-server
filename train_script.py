#!/usr/bin/env python3
"""
Script training mô hình nhận diện thức ăn Việt Nam
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.training.train import train_model
from pathlib import Path

if __name__ == "__main__":
    # Đường dẫn tới dataset
    dataset_dir = "datasets"
    
    print("=== BẮT ĐẦU TRAINING MÔ HÌNH NHẬN DIỆN THỨC ĂN VIỆT NAM ===")
    print(f"Dataset directory: {dataset_dir}")
    
    # Kiểm tra dataset
    if not Path(dataset_dir).exists():
        print(f"❌ Lỗi: Thư mục dataset '{dataset_dir}' không tồn tại!")
        sys.exit(1)
    
    train_dir = Path(dataset_dir) / "train"
    val_dir = Path(dataset_dir) / "val"
    
    if not train_dir.exists():
        print(f"❌ Lỗi: Thư mục training '{train_dir}' không tồn tại!")
        sys.exit(1)
    
    if not val_dir.exists():
        print(f"❌ Lỗi: Thư mục validation '{val_dir}' không tồn tại!")
        sys.exit(1)
    
    # Liệt kê các lớp
    classes = [d.name for d in train_dir.iterdir() if d.is_dir()]
    print(f"📊 Số lớp: {len(classes)}")
    print(f"🏷️  Các lớp: {', '.join(classes)}")
    
    # Đếm số ảnh mỗi lớp
    print("\n📸 Số lượng ảnh mỗi lớp:")
    for cls in classes:
        train_count = len(list((train_dir / cls).glob("*.jpg")) + list((train_dir / cls).glob("*.jpeg")) + list((train_dir / cls).glob("*.png")))
        val_count = len(list((val_dir / cls).glob("*.jpg")) + list((val_dir / cls).glob("*.jpeg")) + list((val_dir / cls).glob("*.png")))
        print(f"  {cls}: {train_count} (train) + {val_count} (val) = {train_count + val_count}")
    
    print(f"\n🚀 Bắt đầu training với:")
    print(f"  - Số epochs: 10")
    print(f"  - Batch size: 16")
    print(f"  - Learning rate: 3e-4")
    print(f"  - Device: CPU")
    
    try:
        # Bắt đầu training
        train_model(
            dataset_dir=dataset_dir,
            num_epochs=10,
            batch_size=16,  # Giảm batch size cho CPU
            learning_rate=3e-4
        )
        print("\n✅ Training hoàn thành thành công!")
        
    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình training: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
