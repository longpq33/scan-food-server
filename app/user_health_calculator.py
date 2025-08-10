from typing import Dict, List
from app.schemas import UserProfile, UserMetrics

class UserHealthCalculator:
    """Tính toán các chỉ số sức khỏe của người dùng"""
    
    @staticmethod
    def calculate_bmi(height_cm: float, weight_kg: float) -> tuple[float, str]:
        """Tính BMI và phân loại"""
        height_m = height_cm / 100
        bmi = weight_kg / (height_m * height_m)
        
        if bmi < 18.5:
            category = "Thiếu cân"
        elif bmi < 25:
            category = "Bình thường"
        elif bmi < 30:
            category = "Thừa cân"
        else:
            category = "Béo phì"
            
        return round(bmi, 1), category
    
    @staticmethod
    def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
        """Tính BMR (Basal Metabolic Rate)"""
        if gender.lower() == "male":
            bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
        
        return round(bmr, 0)
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        """Tính TDEE (Total Daily Energy Expenditure)"""
        activity_multipliers = {
            "sedentary": 1.2,      # Ít vận động
            "light": 1.375,        # Vận động nhẹ
            "moderate": 1.55,      # Vận động vừa phải
            "active": 1.725,       # Vận động nhiều
            "very_active": 1.9     # Vận động rất nhiều
        }
        
        multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
        return round(bmr * multiplier, 0)
    
    @staticmethod
    def calculate_daily_targets(tdee: float, goal: str) -> Dict[str, float]:
        """Tính toán mục tiêu dinh dưỡng hàng ngày"""
        if goal == "lose_weight":
            target_calories = tdee - 500  # Giảm 500 cal/ngày để giảm 0.5kg/tuần
        elif goal == "gain_weight":
            target_calories = tdee + 300  # Tăng 300 cal/ngày để tăng cân
        else:
            target_calories = tdee  # Duy trì cân nặng
        
        # Phân bổ macronutrients
        protein_calories = target_calories * 0.25  # 25% protein
        fat_calories = target_calories * 0.25      # 25% fat
        carbs_calories = target_calories * 0.5     # 50% carbs
        
        return {
            "calories": round(target_calories, 0),
            "protein": round(protein_calories / 4, 1),    # 1g protein = 4 cal
            "fat": round(fat_calories / 9, 1),            # 1g fat = 9 cal
            "carbs": round(carbs_calories / 4, 1)         # 1g carbs = 4 cal
        }
    
    @staticmethod
    def calculate_user_metrics(user_profile: UserProfile) -> UserMetrics:
        """Tính toán tất cả các chỉ số sức khỏe của người dùng"""
        bmi, bmi_category = UserHealthCalculator.calculate_bmi(
            user_profile.height, user_profile.weight
        )
        
        bmr = UserHealthCalculator.calculate_bmr(
            user_profile.weight, user_profile.height, user_profile.age, user_profile.gender
        )
        
        tdee = UserHealthCalculator.calculate_tdee(bmr, user_profile.activity_level)
        
        daily_targets = UserHealthCalculator.calculate_daily_targets(tdee, user_profile.goal)
        
        return UserMetrics(
            bmi=bmi,
            bmi_category=bmi_category,
            bmr=bmr,
            tdee=tdee,
            daily_calories_target=daily_targets["calories"],
            daily_protein_target=daily_targets["protein"],
            daily_carbs_target=daily_targets["carbs"],
            daily_fat_target=daily_targets["fat"]
        )
