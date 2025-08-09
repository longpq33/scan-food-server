# scan-food-server

Backend FastAPI + PyTorch cho nhận diện món ăn Việt, hỗ trợ train/predict và tích hợp mobile.

## Công nghệ sử dụng
- FastAPI (REST API)
- Uvicorn (ASGI server)
- Python 3.11 (khuyến nghị)
- PyTorch + Torchvision (transfer learning MobileNetV3 Small)
- Pillow, NumPy (xử lý ảnh)
- datasets, huggingface_hub (tùy chọn để tải dataset)

## Yêu cầu hệ thống
- Python 3.11 (macOS có thể cài qua `brew install python@3.11`)
- pip, venv
- (Tùy chọn) GPU/CUDA hoặc Metal (MPS) trên Mac để train nhanh hơn

## Cài đặt
```bash
cd server
python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Start server
```bash
# trong thư mục server, đã kích hoạt venv
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# hoặc không dùng reload (ổn định hơn khi chạy nền)
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000
```
- Health check: mở `http://localhost:8000/health`
- OpenAPI docs: `http://localhost:8000/docs`

## Cấu trúc dataset (ImageFolder)
```
server/datasets/
  train/
    bia_333/
    bia_tiger/
    bun_cha/
    goi_cuon/
    pho_bo/
  val/
    bia_333/
    bia_tiger/
    bun_cha/
    goi_cuon/
    pho_bo/
```
Gợi ý: ≥ 50–100 ảnh/lớp để đạt độ chính xác ổn định.

## API
### GET /health
- Trả về: `{ "status": "ok" }`

### POST /predict
- Request: multipart/form-data, key `file` là ảnh
- Response mẫu:
```json
{
  "dish_name": "pho_bo",
  "confidence": 0.87
}
```
- cURL:
```bash
curl -X POST http://localhost:8000/predict \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/absolute/path/to/photo.jpg"
```

### POST /train
- Body JSON:
```json
{
  "dataset_dir": "/absolute/path/to/server/datasets",
  "num_epochs": 10,
  "batch_size": 16,
  "learning_rate": 0.0005
}
```
- Chạy nền, lưu model tốt nhất tại `server/models/best.pt` và nhãn `server/models/labels.txt`.
- cURL:
```bash
curl -X POST http://localhost:8000/train \
  -H 'Content-Type: application/json' \
  -d '{
    "dataset_dir": "/Users/<you>/scan-food/server/datasets",
    "num_epochs": 10,
    "batch_size": 16,
    "learning_rate": 0.0005
  }'
```

## Huấn luyện nhanh (chạy trực tiếp bằng Python)
```bash
source .venv/bin/activate
python -c "from app.training.train import train_model; train_model(dataset_dir='datasets', num_epochs=10, batch_size=16, learning_rate=5e-4)"
```

## Gợi ý nâng cao độ chính xác
- Tăng số ảnh thật/lớp, đa dạng ánh sáng/góc chụp
- Tăng epoch (10–20), batch 16–32 nếu đủ RAM
- Fine-tune sâu hơn: mở/"unfreeze" một số block cuối của backbone

## Tích hợp mobile
- Mobile gọi `POST /predict` (multipart) để nhận `{dish_name, confidence}`
- Đặt endpoint trong app về `http://<IP_máy_server>:8000/predict`
