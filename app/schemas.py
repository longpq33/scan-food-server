from pydantic import BaseModel, Field
from typing import Optional

class TrainRequest(BaseModel):
    dataset_dir: str = Field(..., description="Đường dẫn tuyệt đối tới thư mục dataset")
    num_epochs: Optional[int] = Field(5, ge=1, le=200)
    batch_size: Optional[int] = Field(32, ge=1, le=512)
    learning_rate: Optional[float] = Field(5e-4, gt=0, le=1.0)

class PredictResponse(BaseModel):
    dish_name: str
    confidence: float


class AutoTrainRequest(BaseModel):
    classes: list[str] = Field(..., min_items=1, description="Danh sách lớp cần crawl & train")
    images_per_class: int = Field(30, ge=5, le=200)
    num_epochs: int = Field(5, ge=1, le=200)
    batch_size: int = Field(32, ge=1, le=512)
    learning_rate: float = Field(5e-4, gt=0, le=1.0)
