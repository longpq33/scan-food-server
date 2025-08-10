# 🍎 Nutrition Advisor API - Hệ thống tư vấn dinh dưỡng thông minh

## 📋 Tổng quan

Nutrition Advisor là hệ thống tư vấn dinh dưỡng thông minh, giúp người dùng:
- Tính toán BMI, BMR, TDEE dựa trên thông tin cá nhân
- Phân tích nhu cầu dinh dưỡng hàng ngày
- Đưa ra khuyến nghị về món ăn dựa trên mục tiêu cá nhân
- So sánh dinh dưỡng giữa các món ăn

## 🚀 Các API Endpoints

### 1. Phân tích thông tin cơ thể
**POST** `/nutrition/analyze-body`

Tính toán BMI, BMR, TDEE dựa trên thông tin người dùng.

**Request Body:**
```json
{
  "height": 170,
  "weight": 65,
  "age": 25,
  "gender": "male",
  "activity_level": "moderately_active",
  "goal": "lose_weight"
}
```

**Response:**
```json
{
  "bmi": 22.49,
  "bmi_category": "Bình thường",
  "bmr": 1587,
  "tdee": 2460,
  "daily_calories_target": 2091
}
```

### 2. Tính toán nhu cầu dinh dưỡng hàng ngày
**POST** `/nutrition/daily-needs`

Tính toán nhu cầu protein, carbs, fat, fiber hàng ngày.

**Request Body:** Tương tự như trên

**Response:**
```json
{
  "calories": 2091,
  "protein": 156.8,
  "carbs": 261.4,
  "fat": 58.1,
  "fiber": 52.3
}
```

### 3. Khuyến nghị món ăn
**POST** `/nutrition/food-recommendation?food_name=phở bò`

Đưa ra khuyến nghị về món ăn cụ thể.

**Request Body:** UserProfile
**Query Param:** `food_name` - tên món ăn

**Response:**
```json
{
  "food_name": "Phở bò",
  "should_eat": true,
  "confidence_score": 0.7,
  "reason": "Món ăn này tương đối phù hợp, có thể ăn với điều kiện",
  "warnings": [],
  "suggestions": [
    "Có thể chia nhỏ khẩu phần để giảm calo",
    "Protein cao giúp no lâu, tốt cho cơ bắp"
  ],
  "portion_recommendation": "Có thể ăn bình thường nhưng không nên ăn thêm",
  "daily_impact": {
    "calories": 16.7,
    "protein": 15.9,
    "carbs": 17.2,
    "fat": 13.8,
    "fiber": 5.7
  }
}
```

### 4. Phân tích hoàn chỉnh
**POST** `/nutrition/complete-analysis?food_name=phở bò`

Phân tích toàn diện và đưa ra khuyến nghị chi tiết.

**Response:** Bao gồm tất cả thông tin từ các API trên.

### 5. So sánh nhiều món ăn
**POST** `/nutrition/compare-foods`

So sánh và xếp hạng nhiều món ăn.

**Request Body:**
```json
{
  "user_profile": { ... },
  "food_names": ["phở bò", "bún chả", "bánh mì"]
}
```

### 6. Lấy danh sách mức độ hoạt động
**GET** `/nutrition/activity-levels`

**Response:**
```json
{
  "activity_levels": [
    {
      "value": "sedentary",
      "label": "Ít vận động",
      "description": "Làm việc văn phòng, ít vận động"
    },
    {
      "value": "lightly_active",
      "label": "Vận động nhẹ",
      "description": "Vận động nhẹ 1-3 lần/tuần"
    }
  ]
}
```

### 7. Lấy danh sách mục tiêu dinh dưỡng
**GET** `/nutrition/goals`

**Response:**
```json
{
  "goals": [
    {
      "value": "lose_weight",
      "label": "Giảm cân",
      "description": "Giảm cân an toàn và hiệu quả"
    },
    {
      "value": "build_muscle",
      "label": "Xây dựng cơ bắp",
      "description": "Tăng cơ và sức mạnh"
    }
  ]
}
```

## 🔧 Cách sử dụng

### Bước 1: Khởi động server
```bash
cd server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Bước 2: Test các API
```bash
# Test phân tích cơ thể
curl -X POST "http://localhost:8000/nutrition/analyze-body" \
  -H "Content-Type: application/json" \
  -d '{
    "height": 170,
    "weight": 65,
    "age": 25,
    "gender": "male",
    "activity_level": "moderately_active",
    "goal": "lose_weight"
  }'

# Test khuyến nghị món ăn
curl -X POST "http://localhost:8000/nutrition/food-recommendation?food_name=phở bò" \
  -H "Content-Type: application/json" \
  -d '{
    "height": 170,
    "weight": 65,
    "age": 25,
    "gender": "male",
    "activity_level": "moderately_active",
    "goal": "lose_weight"
  }'
```

### Bước 3: Chạy test script
```bash
cd server
python test_nutrition_advisor.py
```

## 📊 Công thức tính toán

### BMI (Body Mass Index)
```
BMI = Cân nặng (kg) / (Chiều cao (m))²
```

### BMR (Basal Metabolic Rate) - Mifflin-St Jeor
- **Nam:** BMR = 10 × cân nặng + 6.25 × chiều cao - 5 × tuổi + 5
- **Nữ:** BMR = 10 × cân nặng + 6.25 × chiều cao - 5 × tuổi - 161

### TDEE (Total Daily Energy Expenditure)
- **Ít vận động:** BMR × 1.2
- **Vận động nhẹ:** BMR × 1.375
- **Vận động vừa phải:** BMR × 1.55
- **Vận động nhiều:** BMR × 1.725
- **Vận động rất nhiều:** BMR × 1.9

### Điều chỉnh calo theo mục tiêu
- **Giảm cân:** TDEE × 0.85
- **Duy trì:** TDEE × 1.0
- **Tăng cân:** TDEE × 1.15
- **Xây dựng cơ bắp:** TDEE × 1.1

## 🎯 Phân loại BMI

- **Thiếu cân:** < 18.5
- **Bình thường:** 18.5 - 24.9
- **Thừa cân:** 25.0 - 29.9
- **Béo phì độ I:** 30.0 - 34.9
- **Béo phì độ II:** 35.0 - 39.9
- **Béo phì độ III:** ≥ 40.0

## 🔍 Thuật toán khuyến nghị

Hệ thống đánh giá món ăn dựa trên:

1. **Calories:** So sánh với nhu cầu hàng ngày
2. **Protein:** Đánh giá chất lượng dinh dưỡng
3. **Carbs:** Kiểm tra phù hợp với mục tiêu
4. **Fat:** Đánh giá chất béo
5. **Fiber:** Kiểm tra chất xơ
6. **Mục tiêu cá nhân:** Điều chỉnh theo goal

**Điểm tổng thể:** -5 đến +5, chuẩn hóa về 0-1

**Ngưỡng khuyến nghị:** ≥ 0.4 (40%) thì nên ăn

## 📱 Tích hợp với React Native

Các API này có thể dễ dàng tích hợp vào ScanFoodApp để:
- Thu thập thông tin cá nhân người dùng
- Hiển thị phân tích dinh dưỡng chi tiết
- Đưa ra khuyến nghị thông minh
- So sánh các món ăn

## 🚨 Lưu ý

- Tất cả các API đều trả về JSON
- Sử dụng UTF-8 encoding cho tiếng Việt
- Các giá trị số được làm tròn đến 1-2 chữ số thập phân
- Timestamp sử dụng ISO format
- Error handling với HTTP status codes phù hợp
