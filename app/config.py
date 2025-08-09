from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "best.pt"
LABELS_PATH = MODEL_DIR / "labels.txt"

DEFAULT_IMAGE_SIZE = 256
DEFAULT_NUM_EPOCHS = 5
DEFAULT_BATCH_SIZE = 32
DEFAULT_LR = 5e-4
