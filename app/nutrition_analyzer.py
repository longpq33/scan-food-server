"""
Module phân tích dinh dưỡng nâng cao cho các món ăn Việt Nam
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class NutritionAnalysis:
    """Kết quả phân tích dinh dưỡng"""
    food_name: str
    calories: int
    protein: float
    carbs: float
    fat: float
    fiber: float
    sodium: int
    serving_size: str
    health_score: float  # Điểm sức khỏe từ 0-100
    health_tips: List[str]  # Lời khuyên sức khỏe
    daily_value_percentage: Dict[str, float]  # Phần trăm so với nhu cầu hàng ngày
    category: str  # Phân loại món ăn (healthy, moderate, high-calorie)

class NutritionAnalyzer:
    """Phân tích dinh dưỡng cho các món ăn Việt Nam"""
    
    def __init__(self, nutrition_file: str = "datasets/nutrition/vietnamese_foods.json"):
        self.nutrition_file = Path(nutrition_file)
        self.nutrition_data = self._load_nutrition_data()
        
        # Nhu cầu dinh dưỡng hàng ngày (người trưởng thành)
        self.daily_values = {
            "calories": 2000,
            "protein": 50,  # g
            "carbs": 275,   # g
            "fat": 55,      # g
            "fiber": 28,    # g
            "sodium": 2300, # mg
            "vitamin_a": 900,  # mcg
            "vitamin_c": 90,   # mg
            "vitamin_b12": 2.4, # mcg
            "iron": 18,     # mg
            "calcium": 1300, # mg
        }
    
    def _load_nutrition_data(self) -> Dict:
        """Load dữ liệu dinh dưỡng từ file JSON"""
        if not self.nutrition_file.exists():
            return {}
        
        try:
            with open(self.nutrition_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Lỗi khi load file dinh dưỡng: {e}")
            return {}
    
    def analyze_nutrition(self, food_key: str) -> Optional[NutritionAnalysis]:
        """Phân tích dinh dưỡng cho một món ăn"""
        if food_key not in self.nutrition_data:
            return None
        
        food_data = self.nutrition_data[food_key]
        
        # Tính điểm sức khỏe
        health_score = self._calculate_health_score(food_data)
        
        # Tạo lời khuyên sức khỏe
        health_tips = self._generate_health_tips(food_data)
        
        # Tính phần trăm so với nhu cầu hàng ngày
        daily_value_percentage = self._calculate_daily_value_percentage(food_data)
        
        # Phân loại món ăn
        category = self._categorize_food(food_data)
        
        return NutritionAnalysis(
            food_name=food_data["name"],
            calories=food_data["calories"],
            protein=food_data["protein"],
            carbs=food_data["carbs"],
            fat=food_data["fat"],
            fiber=food_data["fiber"],
            sodium=food_data["sodium"],
            serving_size=food_data["serving_size"],
            health_score=health_score,
            health_tips=health_tips,
            daily_value_percentage=daily_value_percentage,
            category=category
        )
    
    def _calculate_health_score(self, food_data: Dict) -> float:
        """Tính điểm sức khỏe từ 0-100"""
        score = 100.0
        
        # Trừ điểm cho calo cao
        if food_data["calories"] > 400:
            score -= 20
        elif food_data["calories"] > 300:
            score -= 10
        
        # Trừ điểm cho natri cao
        if food_data["sodium"] > 1000:
            score -= 15
        elif food_data["sodium"] > 600:
            score -= 8
        
        # Trừ điểm cho chất béo cao
        if food_data["fat"] > 20:
            score -= 15
        elif food_data["fat"] > 15:
            score -= 8
        
        # Cộng điểm cho protein cao
        if food_data["protein"] > 20:
            score += 10
        elif food_data["protein"] > 15:
            score += 5
        
        # Cộng điểm cho chất xơ
        if food_data["fiber"] > 3:
            score += 10
        elif food_data["fiber"] > 1:
            score += 5
        
        return max(0, min(100, score))
    
    def _generate_health_tips(self, food_data: Dict) -> List[str]:
        """Tạo lời khuyên sức khỏe dựa trên dinh dưỡng"""
        tips = []
        
        if food_data["calories"] > 400:
            tips.append("Món ăn này có lượng calo cao, nên ăn vừa phải")
        
        if food_data["sodium"] > 1000:
            tips.append("Hàm lượng natri cao, người bị huyết áp nên hạn chế")
        
        if food_data["protein"] > 20:
            tips.append("Giàu protein, tốt cho việc xây dựng cơ bắp")
        
        if food_data["fiber"] > 3:
            tips.append("Chứa nhiều chất xơ, tốt cho hệ tiêu hóa")
        
        if food_data["fat"] > 20:
            tips.append("Hàm lượng chất béo cao, nên ăn điều độ")
        
        if not tips:
            tips.append("Món ăn cân bằng dinh dưỡng, phù hợp cho bữa ăn hàng ngày")
        
        return tips
    
    def _calculate_daily_value_percentage(self, food_data: Dict) -> Dict[str, float]:
        """Tính phần trăm so với nhu cầu hàng ngày"""
        percentages = {}
        
        for nutrient, value in self.daily_values.items():
            if nutrient in food_data:
                if nutrient == "calories":
                    percentages[nutrient] = (food_data[nutrient] / value) * 100
                elif nutrient in ["protein", "carbs", "fat", "fiber"]:
                    percentages[nutrient] = (food_data[nutrient] / value) * 100
                elif nutrient == "sodium":
                    percentages[nutrient] = (food_data[nutrient] / value) * 100
                elif nutrient == "vitamin_a" and "vitamins" in food_data and "A" in food_data["vitamins"]:
                    percentages[nutrient] = (food_data["vitamins"]["A"] / value) * 100
                elif nutrient == "vitamin_c" and "vitamins" in food_data and "C" in food_data["vitamins"]:
                    percentages[nutrient] = (food_data["vitamins"]["C"] / value) * 100
                elif nutrient == "vitamin_b12" and "vitamins" in food_data and "B12" in food_data["vitamins"]:
                    percentages[nutrient] = (food_data["vitamins"]["B12"] / value) * 100
                elif nutrient == "iron" and "minerals" in food_data and "iron" in food_data["minerals"]:
                    percentages[nutrient] = (food_data["minerals"]["iron"] / value) * 100
                elif nutrient == "calcium" and "minerals" in food_data and "calcium" in food_data["minerals"]:
                    percentages[nutrient] = (food_data["minerals"]["calcium"] / value) * 100
        
        return percentages
    
    def _categorize_food(self, food_data: Dict) -> str:
        """Phân loại món ăn dựa trên dinh dưỡng"""
        if food_data["calories"] <= 200 and food_data["fat"] <= 10:
            return "healthy"
        elif food_data["calories"] <= 350 and food_data["fat"] <= 15:
            return "moderate"
        else:
            return "high-calorie"
    
    def get_nutrition_summary(self, food_key: str) -> Optional[Dict]:
        """Lấy tóm tắt dinh dưỡng cho món ăn"""
        analysis = self.analyze_nutrition(food_key)
        if not analysis:
            return None
        
        return {
            "food_name": analysis.food_name,
            "calories": analysis.calories,
            "protein": analysis.protein,
            "carbs": analysis.carbs,
            "fat": analysis.fat,
            "serving_size": analysis.serving_size,
            "health_score": analysis.health_score,
            "category": analysis.category,
            "health_tips": analysis.health_tips[:2],  # Chỉ lấy 2 tips đầu
            "daily_value_percentage": {
                k: round(v, 1) for k, v in analysis.daily_value_percentage.items()
            }
        }
    
    def get_all_foods_summary(self) -> List[Dict]:
        """Lấy tóm tắt dinh dưỡng cho tất cả món ăn"""
        summaries = []
        for food_key in self.nutrition_data.keys():
            summary = self.get_nutrition_summary(food_key)
            if summary:
                summary["food_key"] = food_key
                summaries.append(summary)
        
        return summaries
