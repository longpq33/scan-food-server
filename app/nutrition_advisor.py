"""
Nutrition Advisor - Hệ thống tư vấn dinh dưỡng thông minh
Tính toán BMI, BMR, TDEE và đưa ra khuyến nghị về món ăn
"""

import math
from datetime import datetime
from typing import Dict, List, Tuple
from .schemas import (
    UserProfile, BodyMetrics, DailyNutritionNeeds, 
    FoodRecommendation, NutritionComparison, CompleteAnalysis,
    NutritionInfo, ActivityLevel, Goal
)


class NutritionAdvisor:
    """Lớp chính để tư vấn dinh dưỡng"""
    
    # Hệ số hoạt động cho TDEE
    ACTIVITY_MULTIPLIERS = {
        ActivityLevel.SEDENTARY: 1.2,           # Ít vận động
        ActivityLevel.LIGHTLY_ACTIVE: 1.375,    # Vận động nhẹ
        ActivityLevel.MODERATELY_ACTIVE: 1.55,  # Vận động vừa phải
        ActivityLevel.VERY_ACTIVE: 1.725,       # Vận động nhiều
        ActivityLevel.EXTREMELY_ACTIVE: 1.9     # Vận động rất nhiều
    }
    
    # Hệ số điều chỉnh calo theo mục tiêu
    GOAL_CALORIE_ADJUSTMENTS = {
        Goal.LOSE_WEIGHT: 0.85,      # Giảm 15% calo
        Goal.MAINTAIN_WEIGHT: 1.0,   # Giữ nguyên
        Goal.GAIN_WEIGHT: 1.15,      # Tăng 15% calo
        Goal.BUILD_MUSCLE: 1.1       # Tăng 10% calo
    }
    
    # Phân loại BMI
    BMI_CATEGORIES = {
        (0, 18.5): "Thiếu cân",
        (18.5, 25): "Bình thường", 
        (25, 30): "Thừa cân",
        (30, 35): "Béo phì độ I",
        (35, 40): "Béo phì độ II",
        (40, float('inf')): "Béo phì độ III"
    }
    
    # Tỷ lệ dinh dưỡng theo mục tiêu
    NUTRITION_RATIOS = {
        Goal.LOSE_WEIGHT: {"protein": 0.3, "carbs": 0.4, "fat": 0.3},
        Goal.MAINTAIN_WEIGHT: {"protein": 0.25, "carbs": 0.5, "fat": 0.25},
        Goal.GAIN_WEIGHT: {"protein": 0.25, "carbs": 0.55, "fat": 0.2},
        Goal.BUILD_MUSCLE: {"protein": 0.35, "carbs": 0.45, "fat": 0.2}
    }

    def calculate_bmi(self, weight: float, height: float) -> float:
        """Tính chỉ số BMI"""
        height_m = height / 100
        return round(weight / (height_m ** 2), 2)

    def get_bmi_category(self, bmi: float) -> str:
        """Phân loại BMI"""
        for (min_bmi, max_bmi), category in self.BMI_CATEGORIES.items():
            if min_bmi <= bmi < max_bmi:
                return category
        return "Không xác định"

    def calculate_bmr(self, weight: float, height: float, age: int, gender: str) -> float:
        """Tính BMR (Basal Metabolic Rate) theo công thức Mifflin-St Jeor"""
        if gender == "male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:  # female
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        return round(bmr)

    def calculate_tdee(self, bmr: float, activity_level: ActivityLevel) -> float:
        """Tính TDEE (Total Daily Energy Expenditure)"""
        multiplier = self.ACTIVITY_MULTIPLIERS[activity_level]
        return round(bmr * multiplier)

    def calculate_daily_calories_target(self, tdee: float, goal: Goal) -> float:
        """Tính mục tiêu calo hàng ngày dựa trên goal"""
        adjustment = self.GOAL_CALORIE_ADJUSTMENTS[goal]
        return round(tdee * adjustment)

    def calculate_daily_nutrition_needs(self, calories: float, goal: Goal) -> DailyNutritionNeeds:
        """Tính nhu cầu dinh dưỡng hàng ngày"""
        ratios = self.NUTRITION_RATIOS[goal]
        
        # Tính protein (1g = 4 calo)
        protein_calories = calories * ratios["protein"]
        protein_grams = protein_calories / 4
        
        # Tính carbs (1g = 4 calo)  
        carbs_calories = calories * ratios["carbs"]
        carbs_grams = carbs_calories / 4
        
        # Tính fat (1g = 9 calo)
        fat_calories = calories * ratios["fat"]
        fat_grams = fat_calories / 9
        
        # Tính fiber (25-30g/1000 calo)
        fiber_grams = max(25, calories / 1000 * 25)
        
        return DailyNutritionNeeds(
            calories=calories,
            protein=round(protein_grams, 1),
            carbs=round(carbs_grams, 1),
            fat=round(fat_grams, 1),
            fiber=round(fiber_grams, 1)
        )

    def analyze_food_nutrition(self, food_nutrition: NutritionInfo, daily_needs: DailyNutritionNeeds) -> Dict[str, Dict[str, any]]:
        """Phân tích dinh dưỡng món ăn so với nhu cầu hàng ngày"""
        comparison = {}
        
        # So sánh calories
        calories_percent = (food_nutrition.calories / daily_needs.calories) * 100
        comparison["calories"] = {
            "food_value": food_nutrition.calories,
            "daily_need": daily_needs.calories,
            "percentage": round(calories_percent, 1),
            "status": "high" if calories_percent > 30 else "moderate" if calories_percent > 15 else "low"
        }
        
        # So sánh protein
        protein_percent = (food_nutrition.protein / daily_needs.protein) * 100
        comparison["protein"] = {
            "food_value": food_nutrition.protein,
            "daily_need": daily_needs.protein,
            "percentage": round(protein_percent, 1),
            "status": "high" if protein_percent > 40 else "moderate" if protein_percent > 20 else "low"
        }
        
        # So sánh carbs
        carbs_percent = (food_nutrition.carbs / daily_needs.carbs) * 100
        comparison["carbs"] = {
            "food_value": food_nutrition.carbs,
            "daily_need": daily_needs.carbs,
            "percentage": round(carbs_percent, 1),
            "status": "high" if carbs_percent > 40 else "moderate" if carbs_percent > 20 else "low"
        }
        
        # So sánh fat
        fat_percent = (food_nutrition.fat / daily_needs.fat) * 100
        comparison["fat"] = {
            "food_value": food_nutrition.fat,
            "daily_need": daily_needs.fat,
            "percentage": round(fat_percent, 1),
            "status": "high" if fat_percent > 40 else "moderate" if fat_percent > 20 else "low"
        }
        
        # So sánh fiber
        fiber_percent = (food_nutrition.fiber / daily_needs.fiber) * 100
        comparison["fiber"] = {
            "food_value": food_nutrition.fiber,
            "daily_need": daily_needs.fiber,
            "percentage": round(fiber_percent, 1),
            "status": "high" if fiber_percent > 40 else "moderate" if fiber_percent > 20 else "low"
        }
        
        return comparison

    def generate_food_recommendation(
        self, 
        food_nutrition: NutritionInfo, 
        daily_needs: DailyNutritionNeeds,
        user_profile: UserProfile,
        comparison: Dict[str, Dict[str, any]]
    ) -> FoodRecommendation:
        """Tạo khuyến nghị về món ăn"""
        
        # Tính điểm tổng thể
        score = 0
        warnings = []
        suggestions = []
        
        # Đánh giá calories
        calories_percent = comparison["calories"]["percentage"]
        if calories_percent > 50:
            score -= 2
            warnings.append(f"Món ăn này chứa {calories_percent:.1f}% nhu cầu calo hàng ngày - quá cao!")
        elif calories_percent > 30:
            score -= 1
            suggestions.append("Có thể chia nhỏ khẩu phần để giảm calo")
        elif calories_percent < 10:
            score += 1
            suggestions.append("Có thể ăn thêm để đảm bảo đủ năng lượng")
        
        # Đánh giá protein
        protein_percent = comparison["protein"]["percentage"]
        if protein_percent > 50:
            score += 1
            suggestions.append("Protein cao giúp no lâu, tốt cho cơ bắp")
        elif protein_percent < 15:
            score -= 1
            suggestions.append("Có thể bổ sung thêm protein từ thịt, cá, trứng")
        
        # Đánh giá carbs
        carbs_percent = comparison["carbs"]["percentage"]
        if carbs_percent > 60:
            score -= 1
            warnings.append("Carbohydrates quá cao có thể ảnh hưởng đến mục tiêu giảm cân")
        elif carbs_percent < 10:
            score += 1
            suggestions.append("Có thể bổ sung carbs từ gạo, bánh mì, rau củ")
        
        # Đánh giá fat
        fat_percent = comparison["fat"]["percentage"]
        if fat_percent > 50:
            score -= 1
            warnings.append("Chất béo quá cao, cần hạn chế")
        elif fat_percent < 10:
            score += 1
            suggestions.append("Có thể bổ sung chất béo tốt từ dầu olive, hạt")
        
        # Đánh giá fiber
        fiber_percent = comparison["fiber"]["percentage"]
        if fiber_percent > 30:
            score += 1
            suggestions.append("Chất xơ cao giúp tiêu hóa tốt")
        elif fiber_percent < 10:
            score -= 1
            suggestions.append("Cần bổ sung thêm rau xanh để tăng chất xơ")
        
        # Điều chỉnh theo mục tiêu
        if user_profile.goal == Goal.LOSE_WEIGHT and calories_percent > 40:
            score -= 2
            warnings.append("Món ăn này có thể cản trở mục tiêu giảm cân")
        elif user_profile.goal == Goal.GAIN_WEIGHT and calories_percent < 20:
            score += 1
            suggestions.append("Món ăn này phù hợp với mục tiêu tăng cân")
        elif user_profile.goal == Goal.BUILD_MUSCLE and protein_percent > 30:
            score += 2
            suggestions.append("Protein cao rất tốt cho việc xây dựng cơ bắp")
        
        # Chuẩn hóa điểm về thang 0-1
        normalized_score = max(0, min(1, (score + 5) / 10))
        
        # Quyết định có nên ăn hay không
        should_eat = normalized_score >= 0.4
        
        # Tạo khuyến nghị về khẩu phần
        if calories_percent > 50:
            portion = "Nên chia nhỏ khẩu phần hoặc ăn một nửa"
        elif calories_percent > 30:
            portion = "Có thể ăn bình thường nhưng không nên ăn thêm"
        else:
            portion = "Có thể ăn bình thường, thậm chí ăn thêm nếu cần"
        
        # Tạo lý do khuyến nghị
        if should_eat:
            if score >= 3:
                reason = "Món ăn này rất phù hợp với nhu cầu dinh dưỡng của bạn"
            elif score >= 0:
                reason = "Món ăn này tương đối phù hợp, có thể ăn với điều kiện"
            else:
                reason = "Mặc dù có một số điểm cần lưu ý, nhưng vẫn có thể ăn"
        else:
            reason = "Món ăn này không phù hợp với mục tiêu dinh dưỡng hiện tại"
        
        return FoodRecommendation(
            food_name=food_nutrition.name,
            should_eat=should_eat,
            confidence_score=normalized_score,
            reason=reason,
            warnings=warnings,
            suggestions=suggestions,
            portion_recommendation=portion,
            daily_impact={
                "calories": round(calories_percent, 1),
                "protein": round(protein_percent, 1),
                "carbs": round(carbs_percent, 1),
                "fat": round(fat_percent, 1),
                "fiber": round(fiber_percent, 1)
            }
        )

    def analyze_user_profile(self, user_profile: UserProfile) -> BodyMetrics:
        """Phân tích thông tin người dùng và tính toán các chỉ số"""
        bmi = self.calculate_bmi(user_profile.weight, user_profile.height)
        bmi_category = self.get_bmi_category(bmi)
        bmr = self.calculate_bmr(user_profile.weight, user_profile.height, user_profile.age, user_profile.gender)
        tdee = self.calculate_tdee(bmr, user_profile.activity_level)
        daily_calories_target = self.calculate_daily_calories_target(tdee, user_profile.goal)
        
        return BodyMetrics(
            bmi=bmi,
            bmi_category=bmi_category,
            bmr=bmr,
            tdee=tdee,
            daily_calories_target=daily_calories_target
        )

    def get_complete_analysis(
        self, 
        user_profile: UserProfile, 
        food_nutrition: NutritionInfo
    ) -> CompleteAnalysis:
        """Tạo phân tích hoàn chỉnh cho khuyến nghị dinh dưỡng"""
        
        # Phân tích thông tin người dùng
        body_metrics = self.analyze_user_profile(user_profile)
        
        # Tính nhu cầu dinh dưỡng hàng ngày
        daily_needs = self.calculate_daily_nutrition_needs(
            body_metrics.daily_calories_target, 
            user_profile.goal
        )
        
        # So sánh dinh dưỡng món ăn
        comparison = self.analyze_food_nutrition(food_nutrition, daily_needs)
        
        # Tạo khuyến nghị
        food_recommendation = self.generate_food_recommendation(
            food_nutrition, daily_needs, user_profile, comparison
        )
        
        # Tạo so sánh dinh dưỡng
        nutrition_comparison = NutritionComparison(
            food_nutrition=food_nutrition,
            user_needs=daily_needs,
            comparison=comparison
        )
        
        return CompleteAnalysis(
            user_profile=user_profile,
            body_metrics=body_metrics,
            daily_needs=daily_needs,
            food_recommendation=food_recommendation,
            nutrition_comparison=nutrition_comparison,
            timestamp=datetime.now().isoformat()
        )


# Tạo instance để sử dụng
nutrition_advisor = NutritionAdvisor()
