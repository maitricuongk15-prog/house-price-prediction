import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib, os, re

# ── 1. Đọc dữ liệu ──────────────────────────────────────
df = pd.read_csv('house.csv')
print(f"📦 Tổng số dòng: {len(df)}")

# ── 2. Trích xuất tỉnh/thành từ Address ─────────────────
CITIES = [
    'Hà Nội', 'TP.HCM', 'Hồ Chí Minh', 'Đà Nẵng',
    'Hải Phòng', 'Cần Thơ', 'Bình Dương', 'Đồng Nai',
    'Khánh Hòa', 'Quảng Ninh', 'Huế', 'Long An',
    'Vũng Tàu', 'Nha Trang',
]

def extract_city(address):
    if pd.isna(address):
        return 'Khác'
    for city in CITIES:
        if city.lower() in str(address).lower():
            return city
    return 'Khác'

df['city'] = df['Address'].apply(extract_city)
print("📍 Phân bổ tỉnh/thành:")
print(df['city'].value_counts())

# ── 3. Làm sạch dữ liệu ─────────────────────────────────
df = df.rename(columns={
    'Area':           'area',
    'Floors':         'floors',
    'Bedrooms':       'bedrooms',
    'Bathrooms':      'bathrooms',
    'Legal status':   'legal_status',
    'Furniture state':'furniture',
    'Price':          'price',
})

# Chỉ giữ các cột cần thiết
df = df[['area', 'floors', 'bedrooms', 'bathrooms',
         'legal_status', 'furniture', 'city', 'price']]

# Xóa dòng thiếu giá hoặc diện tích
df = df.dropna(subset=['price', 'area'])

# Giới hạn giá hợp lý (0.5 – 500 tỷ)
df = df[(df['price'] >= 0.5) & (df['price'] <= 500)]
df = df[(df['area'] >= 10) & (df['area'] <= 5000)]

# Điền giá trị thiếu
df['floors']    = df['floors'].fillna(1)
df['bedrooms']  = df['bedrooms'].fillna(2)
df['bathrooms'] = df['bathrooms'].fillna(1)
df['legal_status'] = df['legal_status'].fillna('Unknown')
df['furniture']    = df['furniture'].fillna('Unknown')

print(f"\n✅ Sau làm sạch: {len(df)} dòng")

# ── 4. Encode categorical ────────────────────────────────
le_city    = LabelEncoder()
le_legal   = LabelEncoder()
le_furnish = LabelEncoder()

df['city_enc']    = le_city.fit_transform(df['city'])
df['legal_enc']   = le_legal.fit_transform(df['legal_status'])
df['furnish_enc'] = le_furnish.fit_transform(df['furniture'])

# ── 5. Train / Test ──────────────────────────────────────
features = ['area', 'floors', 'bedrooms', 'bathrooms',
            'city_enc', 'legal_enc', 'furnish_enc']

X = df[features]
y = df['price']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── 6. Huấn luyện ───────────────────────────────────────
print("\n🤖 Đang huấn luyện mô hình...")
model = GradientBoostingRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    random_state=42
)
model.fit(X_train, y_train)

# ── 7. Đánh giá ─────────────────────────────────────────
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2  = r2_score(y_test, y_pred)
print(f"📊 MAE : {mae:.3f} tỷ VNĐ  (sai số trung bình)")
print(f"📊 R²  : {r2:.3f}           (1.0 = hoàn hảo)")

# ── 8. Lưu model ────────────────────────────────────────
os.makedirs('predictor/ml_model', exist_ok=True)
joblib.dump({
    'model':      model,
    'le_city':    le_city,
    'le_legal':   le_legal,
    'le_furnish': le_furnish,
    'features':   features,
    'cities':     le_city.classes_.tolist(),
}, 'predictor/ml_model/house_model.pkl')

print("\n💾 Đã lưu: predictor/ml_model/house_model.pkl")