from typing import Dict, List
from app.schemas import UserProfile, UserMetrics, FoodRecommendation
from app.user_health_calculator import UserHealthCalculator

class FoodRecommendationService:
    """Dịch vụ tư vấn và khuyến nghị món ăn"""
    
    @staticmethod
    def analyze_food_nutrition(food_nutrition: dict, user_metrics: UserMetrics) -> dict:
        """Phân tích dinh dưỡng món ăn so với nhu cầu người dùng"""
        calories = food_nutrition.get('calories', 0)
        protein = food_nutrition.get('protein', 0)
        carbs = food_nutrition.get('carbs', 0)
        fat = food_nutrition.get('fat', 0)
        
        # Tính phần trăm so với nhu cầu hàng ngày
        calories_percent = (calories / user_metrics.daily_calories_target) * 100 if user_metrics.daily_calories_target > 0 else 0
        protein_percent = (protein / user_metrics.daily_protein_target) * 100 if user_metrics.daily_protein_target > 0 else 0
        carbs_percent = (carbs / user_metrics.daily_carbs_target) * 100 if user_metrics.daily_carbs_target > 0 else 0
        fat_percent = (fat / user_metrics.daily_fat_target) * 100 if user_metrics.daily_fat_target > 0 else 0
        
        return {
            "calories": {
                "value": calories,
                "target": user_metrics.daily_calories_target,
                "percent": round(calories_percent, 1)
            },
            "protein": {
                "value": protein,
                "target": user_metrics.daily_protein_target,
                "percent": round(protein_percent, 1)
            },
            "carbs": {
                "value": carbs,
                "target": user_metrics.daily_carbs_target,
                "percent": round(carbs_percent, 1)
            },
            "fat": {
                "value": fat,
                "target": user_metrics.daily_fat_target,
                "percent": round(fat_percent, 1)
            }
        }
    
    @staticmethod
    def generate_recommendation(user_profile: UserProfile, food_analysis: dict) -> str:
        """Đưa ra khuyến nghị chính"""
        calories_percent = food_analysis["calories"]["percent"]
        
        if user_profile.goal == "lose_weight":
            if calories_percent > 30:
                return "HẠN CHẾ ĂN"
            elif calories_percent > 20:
                return "ĂN VỪA PHẢI"
            else:
                return "NÊN ĂN"
        elif user_profile.goal == "gain_weight":
            if calories_percent < 15:
                return "NÊN ĂN THÊM"
            elif calories_percent < 25:
                return "NÊN ĂN"
            else:
                return "ĂN VỪA PHẢI"
        else:  # maintain
            if calories_percent > 25:
                return "ĂN VỪA PHẢI"
            else:
                return "NÊN ĂN"
    
    @staticmethod
    def generate_detailed_advice(user_profile: UserProfile, food_analysis: dict, user_metrics: UserMetrics) -> List[str]:
        """Tạo lời khuyên chi tiết"""
        advice = []
        
        calories_percent = food_analysis["calories"]["percent"]
        protein_percent = food_analysis["protein"]["percent"]
        carbs_percent = food_analysis["carbs"]["percent"]
        fat_percent = food_analysis["fat"]["percent"]
        
        # Lời khuyên về calories
        if calories_percent > 30:
            advice.append("⚠️ Món ăn này có lượng calo cao, chiếm {:.1f}% nhu cầu hàng ngày".format(calories_percent))
        elif calories_percent < 10:
            advice.append("✅ Món ăn này ít calo, chỉ chiếm {:.1f}% nhu cầu hàng ngày".format(calories_percent))
        
        # Lời khuyên về protein
        if protein_percent > 40:
            advice.append("💪 Protein cao, tốt cho cơ bắp và no lâu")
        elif protein_percent < 15:
            advice.append("🥩 Có thể bổ sung thêm protein từ thịt, cá, trứng")
        
        # Lời khuyên về carbs
        if carbs_percent > 40:
            advice.append("🍞 Carbs cao, nên ăn vào buổi sáng hoặc trước khi tập")
        elif carbs_percent < 20:
            advice.append("🌾 Carbs thấp, phù hợp với chế độ low-carb")
        
        # Lời khuyên về fat
        if fat_percent > 40:
            advice.append("🥑 Chất béo cao, nên ăn vừa phải")
        elif fat_percent < 15:
            advice.append("🥜 Chất béo thấp, có thể bổ sung từ các loại hạt")
        
        # Lời khuyên theo mục tiêu
        if user_profile.goal == "lose_weight":
            if calories_percent > 25:
                advice.append("🎯 Để giảm cân, nên ăn món này vào bữa chính và giảm bữa phụ")
        elif user_profile.goal == "gain_weight":
            if calories_percent < 20:
                advice.append("🎯 Để tăng cân, có thể ăn thêm món này hoặc bổ sung thêm calo")
        
        # Lời khuyên theo BMI
        if user_metrics.bmi_category == "Thừa cân" or user_metrics.bmi_category == "Béo phì":
            advice.append("📊 Với BMI hiện tại, nên ưu tiên món ăn ít calo, nhiều protein")
        elif user_metrics.bmi_category == "Thiếu cân":
            advice.append("📊 Với BMI hiện tại, nên ưu tiên món ăn giàu calo và dinh dưỡng")
        
        return advice
    
    @staticmethod
    def calculate_health_score(user_profile: UserProfile, food_analysis: dict) -> float:
        """Tính điểm sức khỏe của món ăn (0-100)"""
        score = 100
        
        calories_percent = food_analysis["calories"]["percent"]
        protein_percent = food_analysis["protein"]["percent"]
        carbs_percent = food_analysis["carbs"]["percent"]
        fat_percent = food_analysis["fat"]["percent"]
        
        # Trừ điểm nếu calories quá cao
        if calories_percent > 40:
            score -= 20
        elif calories_percent > 30:
            score -= 10
        elif calories_percent > 25:
            score -= 5
        
        # Cộng điểm nếu protein cân bằng
        if 20 <= protein_percent <= 40:
            score += 10
        elif protein_percent < 15:
            score -= 5
        
        # Cộng điểm nếu carbs cân bằng
        if 30 <= carbs_percent <= 50:
            score += 10
        elif carbs_percent > 60:
            score -= 5
        
        # Cộng điểm nếu fat cân bằng
        if 20 <= fat_percent <= 35:
            score += 10
        elif fat_percent > 40:
            score -= 5
        
        # Điểm theo mục tiêu
        if user_profile.goal == "lose_weight" and calories_percent <= 25:
            score += 15
        elif user_profile.goal == "gain_weight" and calories_percent >= 20:
            score += 15
        elif user_profile.goal == "maintain" and 20 <= calories_percent <= 30:
            score += 15
        
        return max(0, min(100, round(score, 1)))
    
    @staticmethod
    def get_food_recommendation(user_profile: UserProfile, food_name: str, food_nutrition: dict) -> FoodRecommendation:
        """Tạo khuyến nghị hoàn chỉnh cho món ăn"""
        # Tính toán metrics người dùng
        user_metrics = UserHealthCalculator.calculate_user_metrics(user_profile)
        
        # Phân tích dinh dưỡng món ăn
        food_analysis = FoodRecommendationService.analyze_food_nutrition(food_nutrition, user_metrics)
        
        # Tạo khuyến nghị
        recommendation = FoodRecommendationService.generate_recommendation(user_profile, food_analysis)
        
        # Tạo lời khuyên chi tiết
        detailed_advice = FoodRecommendationService.generate_detailed_advice(user_profile, food_analysis, user_metrics)
        
        # Tính điểm sức khỏe
        health_score = FoodRecommendationService.calculate_health_score(user_profile, food_analysis)
        
        return FoodRecommendation(
            food_name=food_name,
            user_metrics=user_metrics,
            food_nutrition=food_nutrition,
            analysis=food_analysis,
            recommendation=recommendation,
            detailed_advice=detailed_advice,
            health_score=health_score
        )
