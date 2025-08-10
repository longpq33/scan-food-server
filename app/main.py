from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
from pathlib import Path
import json
from typing import List

from . import inference
from .schemas import (
    TrainRequest, 
    PredictResponse, 
    AutoTrainRequest, 
    NutritionInfo, 
    FoodListResponse,
    NutritionAnalysis,
    NutritionSummary,
    HealthScore,
    CategoryFoods,
    FoodSearch,
    AllNutritionSummaries,
    # New schemas for nutrition advice
    UserProfile,
    UserMetrics,
    FoodRecommendation
)
from .config import MODEL_DIR
from .training.train import train_model
from .training.clean_dataset import clean_dataset
from .training.auto_dataset import build_dataset
from .nutrition_analyzer import NutritionAnalyzer
from .user_health_calculator import UserHealthCalculator
from .food_recommendation_service import FoodRecommendationService

app = FastAPI(title="ScanFood Server", version="0.1.0")

# Khởi tạo nutrition analyzer
nutrition_analyzer = NutritionAnalyzer()

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


@app.get("/nutrition/{food_name}", response_model=NutritionInfo)
async def get_nutrition(food_name: str):
    """Lấy thông tin dinh dưỡng cho món ăn"""
    try:
        nutrition_file = Path.cwd() / "datasets" / "nutrition" / "vietnamese_foods.json"
        if not nutrition_file.exists():
            raise HTTPException(status_code=404, detail="Database dinh dưỡng không tồn tại")
        
        with open(nutrition_file, 'r', encoding='utf-8') as f:
            nutrition_data = json.load(f)
        
        # Tìm kiếm món ăn (không phân biệt hoa thường)
        food_name_lower = food_name.lower()
        for key, data in nutrition_data.items():
            if key.lower() == food_name_lower or data["name"].lower() == food_name_lower:
                return data
        
        # Nếu không tìm thấy, trả về lỗi
        raise HTTPException(status_code=404, detail=f"Không tìm thấy thông tin dinh dưỡng cho: {food_name}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy thông tin dinh dưỡng: {str(e)}")


@app.get("/nutrition", response_model=FoodListResponse)
async def list_all_foods():
    """Liệt kê tất cả các món ăn có trong database dinh dưỡng"""
    try:
        nutrition_file = Path.cwd() / "datasets" / "nutrition" / "vietnamese_foods.json"
        if not nutrition_file.exists():
            raise HTTPException(status_code=404, detail="Database dinh dưỡng không tồn tại")
        
        with open(nutrition_file, 'r', encoding='utf-8') as f:
            nutrition_data = json.load(f)
        
        # Trả về danh sách tên các món ăn
        food_list = [{"key": key, "name": data["name"]} for key, data in nutrition_data.items()]
        return {"foods": food_list}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy danh sách món ăn: {str(e)}")

# === CÁC API ENDPOINTS MỚI CHO PHÂN TÍCH DINH DƯỠNG ===

@app.get("/nutrition/analyze/{food_key}", response_model=NutritionAnalysis)
async def analyze_nutrition(food_key: str):
    """Phân tích dinh dưỡng chi tiết cho một món ăn"""
    try:
        analysis = nutrition_analyzer.analyze_nutrition(food_key)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy món ăn: {food_key}")
        
        return {
            "food_key": food_key,
            "food_name": analysis.food_name,
            "calories": analysis.calories,
            "protein": analysis.protein,
            "carbs": analysis.carbs,
            "fat": analysis.fat,
            "fiber": analysis.fiber,
            "sodium": analysis.sodium,
            "serving_size": analysis.serving_size,
            "health_score": analysis.health_score,
            "health_tips": analysis.health_tips,
            "daily_value_percentage": analysis.daily_value_percentage,
            "category": analysis.category
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi phân tích dinh dưỡng: {str(e)}")

@app.get("/nutrition/summary/{food_key}", response_model=NutritionSummary)
async def get_nutrition_summary(food_key: str):
    """Lấy tóm tắt dinh dưỡng cho một món ăn"""
    try:
        summary = nutrition_analyzer.get_nutrition_summary(food_key)
        if not summary:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy món ăn: {food_key}")
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy tóm tắt dinh dưỡng: {str(e)}")

@app.get("/nutrition/summary", response_model=AllNutritionSummaries)
async def get_all_nutrition_summaries():
    """Lấy tóm tắt dinh dưỡng cho tất cả món ăn"""
    try:
        summaries = nutrition_analyzer.get_all_foods_summary()
        return {"foods": summaries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy tóm tắt dinh dưỡng: {str(e)}")

@app.get("/nutrition/health-score/{food_key}", response_model=HealthScore)
async def get_health_score(food_key: str):
    """Lấy điểm sức khỏe cho một món ăn"""
    try:
        analysis = nutrition_analyzer.analyze_nutrition(food_key)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy món ăn: {food_key}")
        
        return {
            "food_key": food_key,
            "food_name": analysis.food_name,
            "health_score": analysis.health_score,
            "category": analysis.category,
            "health_tips": analysis.health_tips
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy điểm sức khỏe: {str(e)}")

@app.get("/nutrition/category/{category}", response_model=CategoryFoods)
async def get_foods_by_category(category: str):
    """Lấy danh sách món ăn theo phân loại sức khỏe"""
    try:
        valid_categories = ["healthy", "moderate", "high-calorie"]
        if category not in valid_categories:
            raise HTTPException(status_code=400, detail=f"Phân loại không hợp lệ. Chọn một trong: {valid_categories}")
        
        summaries = nutrition_analyzer.get_all_foods_summary()
        filtered_foods = [food for food in summaries if food["category"] == category]
        
        return {
            "category": category,
            "count": len(filtered_foods),
            "foods": filtered_foods
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy món ăn theo phân loại: {str(e)}")

@app.get("/nutrition/search", response_model=FoodSearch)
async def search_foods(query: str):
    """Tìm kiếm món ăn theo tên hoặc mô tả"""
    try:
        summaries = nutrition_analyzer.get_all_foods_summary()
        query_lower = query.lower()
        
        # Tìm kiếm theo tên món ăn hoặc mô tả
        matched_foods = []
        for food in summaries:
            if (query_lower in food["food_name"].lower() or 
                query_lower in food.get("description", "").lower()):
                matched_foods.append(food)
        
        return {
            "query": query,
            "count": len(matched_foods),
            "foods": matched_foods
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tìm kiếm món ăn: {str(e)}")

# ===== NEW NUTRITION ADVISOR ENDPOINTS =====

@app.post("/nutrition/analyze-body", response_model=UserMetrics)
async def analyze_user_body(user_profile: UserProfile):
    """Phân tích thông tin cơ thể người dùng và tính toán BMI, BMR, TDEE"""
    try:
        body_metrics = UserHealthCalculator.calculate_user_metrics(user_profile)
        return body_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi phân tích thông tin cơ thể: {str(e)}")

@app.post("/nutrition/daily-needs", response_model=UserMetrics)
async def calculate_daily_nutrition_needs(user_profile: UserProfile):
    """Tính toán nhu cầu dinh dưỡng hàng ngày dựa trên thông tin cá nhân"""
    try:
        body_metrics = UserHealthCalculator.calculate_user_metrics(user_profile)
        return body_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tính toán nhu cầu dinh dưỡng: {str(e)}")

@app.post("/nutrition/food-recommendation", response_model=FoodRecommendation)
async def get_food_recommendation(user_profile: UserProfile, food_name: str):
    """Đưa ra khuyến nghị về món ăn dựa trên thông tin cá nhân"""
    try:
        # Lấy thông tin dinh dưỡng món ăn
        nutrition_file = Path.cwd() / "datasets" / "nutrition" / "vietnamese_foods.json"
        if not nutrition_file.exists():
            raise HTTPException(status_code=404, detail="Không tìm thấy file dinh dưỡng")
        
        with open(nutrition_file, 'r', encoding='utf-8') as f:
            foods_data = json.load(f)
        
        # Tìm món ăn
        food_nutrition = None
        for food in foods_data:
            if food["name"].lower() == food_name.lower():
                food_nutrition = food
                break
        
        if not food_nutrition:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy món ăn: {food_name}")
        
        # Tạo khuyến nghị sử dụng service mới
        recommendation = FoodRecommendationService.get_food_recommendation(
            user_profile, food_name, food_nutrition
        )
        
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo khuyến nghị: {str(e)}")

@app.post("/nutrition/complete-analysis", response_model=FoodRecommendation)
async def get_complete_nutrition_analysis(user_profile: UserProfile, food_name: str):
    """Phân tích hoàn chỉnh dinh dưỡng và đưa ra khuyến nghị chi tiết"""
    try:
        # Lấy thông tin dinh dưỡng món ăn
        nutrition_file = Path.cwd() / "datasets" / "nutrition" / "vietnamese_foods.json"
        if not nutrition_file.exists():
            raise HTTPException(status_code=404, detail="Không tìm thấy file dinh dưỡng")
        
        with open(nutrition_file, 'r', encoding='utf-8') as f:
            foods_data = json.load(f)
        
        # Tìm món ăn
        food_nutrition = None
        for food in foods_data:
            if food["name"].lower() == food_name.lower():
                food_nutrition = food
                break
        
        if not food_nutrition:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy món ăn: {food_name}")
        
        # Tạo phân tích hoàn chỉnh sử dụng service mới
        complete_analysis = FoodRecommendationService.get_food_recommendation(
            user_profile, food_name, food_nutrition
        )
        
        return complete_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo phân tích hoàn chỉnh: {str(e)}")

@app.post("/nutrition/compare-foods", response_model=List[FoodRecommendation])
async def compare_multiple_foods(user_profile: UserProfile, food_names: List[str]):
    """So sánh nhiều món ăn và đưa ra khuyến nghị"""
    try:
        if len(food_names) < 2:
            raise HTTPException(status_code=400, detail="Cần ít nhất 2 món ăn để so sánh")
        
        if len(food_names) > 5:
            raise HTTPException(status_code=400, detail="Chỉ có thể so sánh tối đa 5 món ăn")
        
        # Lấy thông tin dinh dưỡng
        nutrition_file = Path.cwd() / "datasets" / "nutrition" / "vietnamese_foods.json"
        if not nutrition_file.exists():
            raise HTTPException(status_code=404, detail="Không tìm thấy file dinh dưỡng")
        
        with open(nutrition_file, 'r', encoding='utf-8') as f:
            foods_data = json.load(f)
        
        recommendations = []
        
        for food_name in food_names:
            # Tìm món ăn
            food_nutrition = None
            for food in foods_data:
                if food["name"].lower() == food_name.lower():
                    food_nutrition = food
                    break
            
            if food_nutrition:
                # Tạo khuyến nghị sử dụng service mới
                recommendation = FoodRecommendationService.get_food_recommendation(
                    user_profile, food_name, food_nutrition
                )
                recommendations.append(recommendation)
            else:
                # Tạo khuyến nghị mặc định nếu không tìm thấy món ăn
                recommendations.append(FoodRecommendation(
                    food_name=food_name,
                    user_metrics=UserHealthCalculator.calculate_user_metrics(user_profile),
                    food_nutrition={},
                    analysis={},
                    recommendation="KHÔNG THỂ ĐÁNH GIÁ",
                    detailed_advice=[f"Không có dữ liệu dinh dưỡng cho {food_name}"],
                    health_score=0.0
                ))
        
        # Sắp xếp theo điểm sức khỏe giảm dần
        recommendations.sort(key=lambda x: x.health_score, reverse=True)
        
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi so sánh món ăn: {str(e)}")

@app.post("/nutrition/scan-and-recommend", response_model=FoodRecommendation)
async def scan_food_and_recommend(user_profile: UserProfile, file: UploadFile = File(...)):
    """Nhận diện món ăn từ ảnh và đưa ra khuyến nghị dinh dưỡng"""
    try:
        # Nhận diện món ăn
        content = await file.read()
        img = Image.open(BytesIO(content)).convert("RGB")
        dish_name, confidence = inference.predict(img)
        
        if confidence < 0.5:
            raise HTTPException(status_code=400, detail=f"Không thể nhận diện món ăn với độ tin cậy cao (confidence: {confidence:.2f})")
        
        # Lấy thông tin dinh dưỡng món ăn
        nutrition_file = Path.cwd() / "datasets" / "nutrition" / "vietnamese_foods.json"
        if not nutrition_file.exists():
            raise HTTPException(status_code=404, detail="Không tìm thấy file dinh dưỡng")
        
        with open(nutrition_file, 'r', encoding='utf-8') as f:
            foods_data = json.load(f)
        
        # Tìm món ăn
        food_nutrition = None
        for food in foods_data:
            if food["name"].lower() == dish_name.lower():
                food_nutrition = food
                break
        
        if not food_nutrition:
            # Nếu không tìm thấy, tạo thông tin mặc định
            food_nutrition = {
                "name": dish_name,
                "calories": 300,  # Giá trị mặc định
                "protein": 15,
                "carbs": 40,
                "fat": 10,
                "fiber": 3,
                "sugar": 5,
                "sodium": 500
            }
        
        # Tạo khuyến nghị dinh dưỡng
        recommendation = FoodRecommendationService.get_food_recommendation(
            user_profile, dish_name, food_nutrition
        )
        
        return recommendation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý ảnh và tạo khuyến nghị: {str(e)}")

@app.get("/nutrition/activity-levels")
async def get_activity_levels():
    """Lấy danh sách các mức độ hoạt động thể chất"""
    return {
        "activity_levels": [
            {"value": "sedentary", "label": "Ít vận động", "description": "Làm việc văn phòng, ít vận động"},
            {"value": "light", "label": "Vận động nhẹ", "description": "Vận động nhẹ 1-3 lần/tuần"},
            {"value": "moderate", "label": "Vận động vừa phải", "description": "Vận động vừa phải 3-5 lần/tuần"},
            {"value": "active", "label": "Vận động nhiều", "description": "Vận động mạnh 6-7 lần/tuần"},
            {"value": "very_active", "label": "Vận động rất nhiều", "description": "Vận động rất mạnh, thể thao chuyên nghiệp"}
        ]
    }

@app.get("/nutrition/goals")
async def get_nutrition_goals():
    """Lấy danh sách các mục tiêu dinh dưỡng"""
    return {
        "goals": [
            {"value": "lose_weight", "label": "Giảm cân", "description": "Giảm cân an toàn và hiệu quả"},
            {"value": "maintain", "label": "Duy trì cân nặng", "description": "Giữ cân nặng hiện tại"},
            {"value": "gain_weight", "label": "Tăng cân", "description": "Tăng cân lành mạnh"}
        ]
    }
