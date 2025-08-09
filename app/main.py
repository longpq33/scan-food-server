from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
from pathlib import Path

from . import inference
from .schemas import TrainRequest, PredictResponse, AutoTrainRequest
from .config import MODEL_DIR
from .training.train import train_model
from .training.clean_dataset import clean_dataset
from .training.auto_dataset import build_dataset

app = FastAPI(title="ScanFood Server", version="0.1.0")


@app.on_event("startup")
async def startup_event():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    inference.load_model()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
async def predict(file: UploadFile = File(...)):
    try:
        content = await file.read()
        img = Image.open(BytesIO(content)).convert("RGB")
        dish, score = inference.predict(img)
        return PredictResponse(dish_name=dish, confidence=score)
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/train")
async def train(req: TrainRequest, background_tasks: BackgroundTasks):
    dataset_dir = Path(req.dataset_dir)
    if not dataset_dir.exists():
        raise HTTPException(status_code=400, detail=f"dataset_dir không tồn tại: {dataset_dir}")

    # chạy nền để không block request
    background_tasks.add_task(
        train_model,
        dataset_dir=str(dataset_dir),
        num_epochs=req.num_epochs or 5,
        batch_size=req.batch_size or 32,
        learning_rate=req.learning_rate or 5e-4,
    )
    return JSONResponse({"status": "training_started"})


@app.post("/autotrain")
async def autotrain(req: AutoTrainRequest, background_tasks: BackgroundTasks):
    base_dataset_dir = Path.cwd() / "datasets"
    base_dataset_dir.mkdir(parents=True, exist_ok=True)

    # Crawl ảnh
    built_dir = build_dataset(base_dataset_dir, req.classes, images_per_class=req.images_per_class)

    # Clean dataset trước khi train
    deleted, scanned = clean_dataset(built_dir)
    print(f"[CLEAN_DATASET] deleted={deleted} / scanned={scanned}")

    # Train nền
    background_tasks.add_task(
        train_model,
        dataset_dir=built_dir,
        num_epochs=req.num_epochs,
        batch_size=req.batch_size,
        learning_rate=req.learning_rate,
    )
    return JSONResponse({"status": "autotrain_started", "dataset_dir": built_dir})
