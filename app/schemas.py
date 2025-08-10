from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

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


class NutritionInfo(BaseModel):
    name: str
    calories: int
    protein: float
    carbs: float
    fat: float
    fiber: float
    sodium: int
    serving_size: str
    ingredients: list[str]
    vitamins: dict[str, float]
    minerals: dict[str, float]
    description: str


class FoodListResponse(BaseModel):
    foods: list[dict[str, str]]

class NutritionAnalysis(BaseModel):
    """Schema cho phân tích dinh dưỡng chi tiết"""
    food_key: str
    food_name: str
    calories: int
    protein: float
    carbs: float
    fat: float
    fiber: float
    sodium: int
    serving_size: str
    health_score: float
    health_tips: List[str]
    daily_value_percentage: Dict[str, float]
    category: str

class NutritionSummary(BaseModel):
    """Schema cho tóm tắt dinh dưỡng"""
    food_key: str
    food_name: str
    calories: int
    protein: float
    carbs: float
    fat: float
    serving_size: str
    health_score: float
    category: str
    health_tips: List[str]
    daily_value_percentage: Dict[str, float]

class HealthScore(BaseModel):
    """Schema cho điểm sức khỏe"""
    food_key: str
    food_name: str
    health_score: float
    category: str
    health_tips: List[str]

class CategoryFoods(BaseModel):
    """Schema cho danh sách món ăn theo phân loại"""
    category: str
    count: int
    foods: List[NutritionSummary]

class FoodSearch(BaseModel):
    """Schema cho kết quả tìm kiếm món ăn"""
    query: str
    count: int
    foods: List[NutritionSummary]

class AllNutritionSummaries(BaseModel):
    """Schema cho tất cả tóm tắt dinh dưỡng"""
    foods: List[NutritionSummary]

# ===== SCHEMAS FOR USER PROFILE AND FOOD RECOMMENDATION =====

class ActivityLevel(str, Enum):
    """Mức độ hoạt động thể chất"""
    SEDENTARY = "sedentary"  # Ít vận động
    LIGHT = "light"  # Vận động nhẹ
    MODERATE = "moderate"  # Vận động vừa phải
    ACTIVE = "active"  # Vận động nhiều
    VERY_ACTIVE = "very_active"  # Vận động rất nhiều

class Goal(str, Enum):
    """Mục tiêu dinh dưỡng"""
    LOSE_WEIGHT = "lose_weight"  # Giảm cân
    MAINTAIN = "maintain"  # Duy trì cân nặng
    GAIN_WEIGHT = "gain_weight"  # Tăng cân

class Gender(str, Enum):
    """Giới tính"""
    MALE = "male"
    FEMALE = "female"

class UserProfile(BaseModel):
    """Thông tin cá nhân người dùng"""
    height: float = Field(..., gt=0, le=300, description="Chiều cao (cm)")
    weight: float = Field(..., gt=0, le=500, description="Cân nặng (kg)")
    age: int = Field(..., gt=0, le=120, description="Tuổi")
    gender: Gender = Field(..., description="Giới tính")
    activity_level: ActivityLevel = Field(..., description="Mức độ hoạt động")
    goal: Goal = Field(..., description="Mục tiêu dinh dưỡng")

class UserMetrics(BaseModel):
    """Các chỉ số cơ thể đã tính toán"""
    bmi: float = Field(..., description="Chỉ số BMI")
    bmi_category: str = Field(..., description="Phân loại BMI")
    bmr: float = Field(..., description="Tỷ lệ trao đổi chất cơ bản (calories/ngày)")
    tdee: float = Field(..., description="Tổng năng lượng tiêu thụ hàng ngày (calories/ngày)")
    daily_calories_target: float = Field(..., description="Mục tiêu calo hàng ngày dựa trên goal")
    daily_protein_target: float = Field(..., description="Mục tiêu protein hàng ngày (g)")
    daily_carbs_target: float = Field(..., description="Mục tiêu carbs hàng ngày (g)")
    daily_fat_target: float = Field(..., description="Mục tiêu fat hàng ngày (g)")

class FoodRecommendation(BaseModel):
    """Khuyến nghị về món ăn"""
    food_name: str = Field(..., description="Tên món ăn")
    user_metrics: UserMetrics = Field(..., description="Chỉ số sức khỏe người dùng")
    food_nutrition: dict = Field(..., description="Thông tin dinh dưỡng món ăn")
    analysis: dict = Field(..., description="Phân tích dinh dưỡng")
    recommendation: str = Field(..., description="Khuyến nghị chính")
    detailed_advice: List[str] = Field(..., description="Lời khuyên chi tiết")
    health_score: float = Field(..., ge=0, le=100, description="Điểm sức khỏe (0-100)")
