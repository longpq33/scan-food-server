"""
Test script cho Nutrition Advisor
Kiểm tra các chức năng tính toán BMI, BMR, TDEE và tư vấn dinh dưỡng
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.nutrition_advisor import nutrition_advisor
from app.schemas import UserProfile, ActivityLevel, Goal, Gender

def test_bmi_calculation():
    """Test tính toán BMI"""
    print("=== Test tính toán BMI ===")
    
    # Test case 1: Người bình thường
    height = 170  # cm
    weight = 65   # kg
    bmi = nutrition_advisor.calculate_bmi(weight, height)
    category = nutrition_advisor.get_bmi_category(bmi)
    
    print(f"Chiều cao: {height}cm, Cân nặng: {weight}kg")
    print(f"BMI: {bmi}")
    print(f"Phân loại: {category}")
    print()
    
    # Test case 2: Người thừa cân
    height = 165
    weight = 80
    bmi = nutrition_advisor.calculate_bmi(weight, height)
    category = nutrition_advisor.get_bmi_category(bmi)
    
    print(f"Chiều cao: {height}cm, Cân nặng: {weight}kg")
    print(f"BMI: {bmi}")
    print(f"Phân loại: {category}")
    print()

def test_bmr_tdee_calculation():
    """Test tính toán BMR và TDEE"""
    print("=== Test tính toán BMR và TDEE ===")
    
    # Test case: Nam, 25 tuổi, 170cm, 65kg, vận động vừa phải
    user_profile = UserProfile(
        height=170,
        weight=65,
        age=25,
        gender=Gender.MALE,
        activity_level=ActivityLevel.MODERATELY_ACTIVE,
        goal=Goal.MAINTAIN_WEIGHT
    )
    
    body_metrics = nutrition_advisor.analyze_user_profile(user_profile)
    
    print(f"Thông tin người dùng:")
    print(f"- Chiều cao: {user_profile.height}cm")
    print(f"- Cân nặng: {user_profile.weight}kg")
    print(f"- Tuổi: {user_profile.age}")
    print(f"- Giới tính: {user_profile.gender.value}")
    print(f"- Mức độ hoạt động: {user_profile.activity_level.value}")
    print(f"- Mục tiêu: {user_profile.goal.value}")
    print()
    
    print(f"Kết quả phân tích:")
    print(f"- BMI: {body_metrics.bmi}")
    print(f"- Phân loại BMI: {body_metrics.bmi_category}")
    print(f"- BMR: {body_metrics.bmr} calories/ngày")
    print(f"- TDEE: {body_metrics.tdee} calories/ngày")
    print(f"- Mục tiêu calo: {body_metrics.daily_calories_target} calories/ngày")
    print()

def test_daily_nutrition_needs():
    """Test tính toán nhu cầu dinh dưỡng hàng ngày"""
    print("=== Test tính toán nhu cầu dinh dưỡng ===")
    
    # Test các mục tiêu khác nhau
    goals = [Goal.LOSE_WEIGHT, Goal.MAINTAIN_WEIGHT, Goal.GAIN_WEIGHT, Goal.BUILD_MUSCLE]
    base_calories = 2000
    
    for goal in goals:
        daily_needs = nutrition_advisor.calculate_daily_nutrition_needs(base_calories, goal)
        
        print(f"Mục tiêu: {goal.value}")
        print(f"- Calories: {daily_needs.calories}")
        print(f"- Protein: {daily_needs.protein}g")
        print(f"- Carbs: {daily_needs.carbs}g")
        print(f"- Fat: {daily_needs.fat}g")
        print(f"- Fiber: {daily_needs.fiber}g")
        print()

def test_food_recommendation():
    """Test tạo khuyến nghị về món ăn"""
    print("=== Test tạo khuyến nghị món ăn ===")
    
    # Tạo user profile mẫu
    user_profile = UserProfile(
        height=170,
        weight=65,
        age=25,
        gender=Gender.MALE,
        activity_level=ActivityLevel.MODERATELY_ACTIVE,
        goal=Goal.LOSE_WEIGHT
    )
    
    # Tạo thông tin dinh dưỡng món ăn mẫu (phở bò)
    from app.schemas import NutritionInfo
    
    pho_bo = NutritionInfo(
        name="Phở bò",
        calories=350,
        protein=25,
        carbs=45,
        fat=8,
        fiber=3,
        sodium=800,
        serving_size="1 tô vừa",
        ingredients=["bánh phở", "thịt bò", "nước dùng", "rau thơm"],
        vitamins={"B12": 2.5, "Iron": 3.2},
        minerals={"Iron": 3.2, "Zinc": 2.1},
        description="Món phở truyền thống Việt Nam"
    )
    
    # Phân tích và tạo khuyến nghị
    body_metrics = nutrition_advisor.analyze_user_profile(user_profile)
    daily_needs = nutrition_advisor.calculate_daily_nutrition_needs(
        body_metrics.daily_calories_target, 
        user_profile.goal
    )
    
    comparison = nutrition_advisor.analyze_food_nutrition(pho_bo, daily_needs)
    recommendation = nutrition_advisor.generate_food_recommendation(
        pho_bo, daily_needs, user_profile, comparison
    )
    
    print(f"Phân tích món ăn: {pho_bo.name}")
    print(f"- Calories: {pho_bo.calories} ({comparison['calories']['percentage']:.1f}% nhu cầu)")
    print(f"- Protein: {pho_bo.protein}g ({comparison['protein']['percentage']:.1f}% nhu cầu)")
    print(f"- Carbs: {pho_bo.carbs}g ({comparison['carbs']['percentage']:.1f}% nhu cầu)")
    print(f"- Fat: {pho_bo.fat}g ({comparison['fat']['percentage']:.1f}% nhu cầu)")
    print()
    
    print(f"Khuyến nghị:")
    print(f"- Có nên ăn: {'Có' if recommendation.should_eat else 'Không'}")
    print(f"- Điểm tin cậy: {recommendation.confidence_score:.2f}")
    print(f"- Lý do: {recommendation.reason}")
    print(f"- Khuyến nghị khẩu phần: {recommendation.portion_recommendation}")
    
    if recommendation.warnings:
        print(f"- Cảnh báo:")
        for warning in recommendation.warnings:
            print(f"  + {warning}")
    
    if recommendation.suggestions:
        print(f"- Gợi ý:")
        for suggestion in recommendation.suggestions:
            print(f"  + {suggestion}")
    
    print(f"- Tác động hàng ngày:")
    for nutrient, percentage in recommendation.daily_impact.items():
        print(f"  + {nutrient}: {percentage}%")

def test_complete_analysis():
    """Test phân tích hoàn chỉnh"""
    print("\n=== Test phân tích hoàn chỉnh ===")
    
    user_profile = UserProfile(
        height=170,
        weight=65,
        age=25,
        gender=Gender.MALE,
        activity_level=ActivityLevel.MODERATELY_ACTIVE,
        goal=Goal.LOSE_WEIGHT
    )
    
    pho_bo = NutritionInfo(
        name="Phở bò",
        calories=350,
        protein=25,
        carbs=45,
        fat=8,
        fiber=3,
        sodium=800,
        serving_size="1 tô vừa",
        ingredients=["bánh phở", "thịt bò", "nước dùng", "rau thơm"],
        vitamins={"B12": 2.5, "Iron": 3.2},
        minerals={"Iron": 3.2, "Zinc": 2.1},
        description="Món phở truyền thống Việt Nam"
    )
    
    complete_analysis = nutrition_advisor.get_complete_analysis(user_profile, pho_bo)
    
    print(f"Phân tích hoàn chỉnh cho {complete_analysis.food_recommendation.food_name}")
    print(f"- BMI: {complete_analysis.body_metrics.bmi} ({complete_analysis.body_metrics.bmi_category})")
    print(f"- BMR: {complete_analysis.body_metrics.bmr} calories/ngày")
    print(f"- TDEE: {complete_analysis.body_metrics.tdee} calories/ngày")
    print(f"- Mục tiêu calo: {complete_analysis.body_metrics.daily_calories_target} calories/ngày")
    print()
    
    print(f"Nhu cầu dinh dưỡng hàng ngày:")
    print(f"- Calories: {complete_analysis.daily_needs.calories}")
    print(f"- Protein: {complete_analysis.daily_needs.protein}g")
    print(f"- Carbs: {complete_analysis.daily_needs.carbs}g")
    print(f"- Fat: {complete_analysis.daily_needs.fat}g")
    print(f"- Fiber: {complete_analysis.daily_needs.fiber}g")
    print()
    
    print(f"Khuyến nghị cuối cùng:")
    print(f"- {complete_analysis.food_recommendation.reason}")
    print(f"- Điểm tin cậy: {complete_analysis.food_recommendation.confidence_score:.2f}")

if __name__ == "__main__":
    print("🚀 Bắt đầu test Nutrition Advisor...\n")
    
    try:
        test_bmi_calculation()
        test_bmr_tdee_calculation()
        test_daily_nutrition_needs()
        test_food_recommendation()
        test_complete_analysis()
        
        print("\n✅ Tất cả test đều thành công!")
        
    except Exception as e:
        print(f"\n❌ Có lỗi xảy ra: {str(e)}")
        import traceback
        traceback.print_exc()
